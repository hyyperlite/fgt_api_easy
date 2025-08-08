#!/usr/bin/env python3
"""
Natural Language Interface for FortiGate API Client

Provides an interactive shell for intelligent parsing of natural language commands.
This module has been refactored to use the new enhanced AI/ML pipeline.
"""

import re
import os
import json
import glob
import logging
import readline
from typing import Dict, List, Optional, Tuple, Any
import configparser
from pathlib import Path

# Import the canonical UserIntent dataclass
from .user_intent import UserIntent

# Attempt to import the real AI components.
# If they fail, the rest of the file will use fallback mechanisms.
try:
    from .ai_formatter import AIDataFormatter
    from .enhanced_intent_classifier import classify_user_intent
    ENHANCED_ML_AVAILABLE = True
    logging.info("Successfully imported AI components.")
except ImportError as e:
    ENHANCED_ML_AVAILABLE = False
    logging.warning(f"Could not import AI components: {e}. Interactive mode will have limited functionality.")
    # Define dummy fallbacks for type hinting purposes if imports fail.
    # These will not be executed because of the ENHANCED_ML_AVAILABLE flag.
    def classify_user_intent(user_query: str, endpoint: Optional[str] = None) -> Optional[UserIntent]:
        raise NotImplementedError("AI components not available.")
    class AIDataFormatter:
        def format_data(self, data: Any, intent: UserIntent) -> str:
            raise NotImplementedError("AI components not available.")


class NaturalLanguageInterface:
    """
    Manages the interactive AI session for the FortiGate API client.
    It loads host configurations and orchestrates the command processing
    using the enhanced AI/ML pipeline.
    """
    
    def __init__(self, host_files: Optional[List[str]] = None):
        """
        Initialize the natural language interface.
        
        Args:
            host_files: List of host configuration files or directories to load.
                       If None, loads from default config directory.
        """
        self.host_files = host_files
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.WARNING)
        
        self.hosts = self._load_host_configs()
    
    def _load_host_configs(self) -> Dict[str, Dict]:
        """Load host configurations from specified files/directories or default config directory."""
        hosts = {}
        
        if self.host_files:
            found_configs = []
            for host_file in self.host_files:
                if os.path.isdir(host_file):
                    for pattern in ['*.json', '*.ini']:
                        found_configs.extend(glob.glob(os.path.join(host_file, pattern)))
                elif os.path.isfile(host_file):
                    found_configs.append(host_file)
                else:
                    self.logger.warning(f"Host file/directory not found: {host_file}")
        else:
            search_dir = './config'
            found_configs = []
            if os.path.exists(search_dir):
                for pattern in ['*.json', '*.ini']:
                    found_configs.extend(glob.glob(os.path.join(search_dir, pattern)))
        
        for config_file in set(found_configs):
            try:
                hosts_from_file = self._parse_config_file(config_file)
                if hosts_from_file:
                    hosts.update(hosts_from_file)
            except Exception as e:
                self.logger.debug(f"Could not parse {config_file}: {e}")
        
        if hosts:
            self.logger.info(f"Found {len(hosts)} host configuration(s).")
        else:
            self.logger.info("No host configurations found.")
        
        return hosts
    
    def _parse_config_file(self, config_file: str) -> Dict[str, Dict]:
        """Parse a config file and extract valid host configurations."""
        hosts = {}
        file_ext = os.path.splitext(config_file)[1].lower()
        
        try:
            if file_ext == '.json':
                with open(config_file, 'r') as f:
                    data = json.load(f)
                hosts = data.get('hosts', data)
            elif file_ext == '.ini':
                config = configparser.ConfigParser()
                config.read(config_file)
                hosts = {s: dict(config.items(s)) for s in config.sections()}
        except Exception as e:
            self.logger.debug(f"Failed to parse {config_file}: {e}")
            return {}

        valid_hosts = {}
        for name, config in hosts.items():
            if self._is_valid_host_config(name, config):
                valid_hosts[name] = self._normalize_host_config(name, config)
        
        return valid_hosts

    def _is_valid_host_config(self, name: str, config: Dict) -> bool:
        """Check if host config has required fields: name, ip/host, apikey."""
        if not isinstance(config, dict):
            return False
        has_ip = any(key in config for key in ['ip', 'host', 'hostname', 'address'])
        has_apikey = any(key in config for key in ['apikey', 'api_key', 'key', 'token'])
        has_name = bool(name or config.get('name'))
        return has_ip and has_apikey and has_name
    
    def _normalize_host_config(self, name: str, config: Dict) -> Dict:
        """Normalize host config to a standard format."""
        normalized = {'name': name}
        for ip_key in ['ip', 'host', 'hostname', 'address']:
            if ip_key in config:
                normalized['ip'] = config[ip_key]
                break
        for key_field in ['apikey', 'api_key', 'key', 'token']:
            if key_field in config:
                normalized['apikey'] = config[key_field]
                break
        for field in ['port', 'timeout', 'verify_ssl', 'vdom']:
            if field in config:
                normalized[field] = config[field]
        return normalized

    def _extract_host(self, command: str) -> Tuple[Optional[str], Optional[Dict], float]:
        """Extract host information from command using regex."""
        command_lower = command.lower()
        
        # Pattern: from host <name>
        match = re.search(r'from host (\w+)', command_lower)
        if match:
            host_name = match.group(1)
            if host_name in self.hosts:
                return host_name, self.hosts[host_name], 1.0
            return host_name, None, 0.8

        # Pattern: from <name> (where name is a known host)
        match = re.search(r'from (\w+)', command_lower)
        if match:
            potential_host = match.group(1)
            if potential_host in self.hosts:
                return potential_host, self.hosts[potential_host], 0.9

        # Pattern: from <ip_address>
        match = re.search(r'from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', command_lower)
        if match:
            ip = match.group(1)
            for name, config in self.hosts.items():
                if config.get('ip') == ip:
                    return name, config, 1.0
            return ip, {'name': ip, 'ip': ip, 'apikey': None}, 0.5
        
        return None, None, 0.0

    def execute_intent_command(self, intent: UserIntent, host_config: Dict) -> Tuple[bool, str]:
        """Executes a command based on a UserIntent object."""
        if not ENHANCED_ML_AVAILABLE:
            return False, "Cannot execute command: AI components are not available."
        try:
            # Import here to avoid issues with circular dependencies or package structure
            from fgt_api_client import FortiGateAPIClient
            
            if not host_config or not host_config.get('ip') or not host_config.get('apikey'):
                return False, "❌ Invalid or incomplete host configuration provided."
            
            client = FortiGateAPIClient(
                host=host_config['ip'],
                apikey=host_config['apikey'],
                use_ssl=True,
                verify_ssl=False,
                timeout=30,
                debug=False
            )
            
            status_code, raw_response = client.execute_request(
                method=intent.method,
                endpoint=intent.endpoint
            )
            
            if status_code != 200:
                return False, f"❌ API call failed (status {status_code}): {raw_response}"
            
            ai_formatter = AIDataFormatter()
            ai_output = ai_formatter.format_data(raw_response, intent)
            return True, ai_output
            
        except Exception as e:
            import traceback
            self.logger.error(f"Error during command execution: {traceback.format_exc()}")
            return False, f"❌ Error executing command: {e}"
    
    def get_interpretation_summary(self, intent: UserIntent, host_name: Optional[str] = None) -> str:
        """Generate a human-readable interpretation summary from a UserIntent object."""
        summary = [f"🤖 Interpretation (confidence: {intent.confidence:.1%}):"]
        summary.append(f"   Action: {intent.method.upper()}")
        summary.append(f"   Target: {intent.endpoint} (conf: {intent.endpoint_confidence:.1%})")
        
        if host_name:
            summary.append(f"   Host: {host_name}")

        if intent.format_type != 'auto':
            summary.append(f"   Format: {intent.format_type} (conf: {intent.format_confidence:.1%})")
        
        if intent.requested_fields:
            summary.append(f"   Fields: {', '.join(intent.requested_fields)} (conf: {intent.field_confidence:.1%})")
        else:
            summary.append("   Fields: auto-select")
            
        if intent.filter_conditions:
            filters_str = ', '.join([f'{f.get("field", "?")} {f.get("operator", "?")} {f.get("value", "?")}' for f in intent.filter_conditions])
            summary.append(f"   Filters: {filters_str} (conf: {intent.filter_confidence:.1%})")
        else:
            summary.append("   Filters: none")
            
        summary.append(f"   Original Request: \"{intent.original_query}\"")
        return "\n".join(summary)

    def list_configured_hosts(self) -> str:
        """List all configured hosts."""
        if not self.hosts:
            return "No hosts configured yet."
        
        lines = ["🏠 Configured Hosts:"]
        for host_name, config in self.hosts.items():
            lines.append(f"   📍 {host_name}: {config.get('ip', 'IP not set')}")
        return "\n".join(lines)


def setup_interactive_readline():
    """Setup readline for command history and editing."""
    try:
        history_file = os.path.expanduser('~/.fgt_history')
        
        if os.path.exists(history_file):
            readline.read_history_file(history_file)
        
        readline.set_history_length(1000)
        
        import atexit
        atexit.register(readline.write_history_file, history_file)
        
        readline.parse_and_bind("tab: complete")
        readline.parse_and_bind("set editing-mode emacs")
        return True
    except (ImportError, AttributeError):
        return False


def interactive_session(nl_interface: NaturalLanguageInterface, host_files: Optional[List[str]] = None):
    """Run an interactive natural language session."""
    has_readline = setup_interactive_readline()
    
    print("🤖 FortiGate API Client - Interactive AI Mode")
    print("=" * 60)
    if not ENHANCED_ML_AVAILABLE:
        print("⚠️  Warning: AI/ML components not found. Functionality will be limited.")
    print("Enter natural language commands or type 'help' for examples.")
    print("Type 'quit' or 'exit' to end the session.")
    if has_readline:
        print("💡 Use ↑/↓ arrows for history, Ctrl+R for search.")
    print()
    
    if host_files:
        print(f"📂 Using host configs from: {', '.join(host_files)}")
    else:
        print("📂 Using default config directory: ./config/")
    
    if nl_interface.hosts:
        print(f"📍 Available hosts: {', '.join(nl_interface.hosts.keys())}")
    else:
        print("📝 No hosts found. Create JSON/INI config files with name, ip, and apikey.")
    print()
    
    session_stats = {'commands': 0, 'successful': 0}
    
    while True:
        try:
            command = input("🔤 fgt> ").strip()
            
            if not command:
                continue
            
            cmd_lower = command.lower()
            if cmd_lower in ['quit', 'exit', 'q']:
                break
            
            if cmd_lower == 'help':
                show_interactive_help()
                continue
            
            if cmd_lower == 'hosts':
                print(nl_interface.list_configured_hosts())
                continue
            
            if cmd_lower == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                continue
            
            session_stats['commands'] += 1
            print(f"\n🤖 Processing: \"{command}\"")
            
            # Step 1: Classify intent
            if not ENHANCED_ML_AVAILABLE:
                print("❌ AI classifier not available. Cannot process natural language.")
                continue
                
            intent = classify_user_intent(command)
            if not intent:
                print("❌ Could not understand the command. Please try rephrasing.")
                continue

            # Step 2: Extract host
            host_name, host_config, _ = nl_interface._extract_host(command)
            print(nl_interface.get_interpretation_summary(intent, host_name))

            # Step 3: Validate host
            if not host_config or not host_config.get('apikey'):
                print(f"❌ Host '{host_name or 'not specified'}' is not configured or missing an API key.")
                print("💡 Use 'from host <name>' and ensure the host is in your config files.")
                continue

            # Step 4: Execute
            print("🔄 Executing API call...")
            success, output = nl_interface.execute_intent_command(intent, host_config)
            
            if success:
                print("✅ Command executed successfully.")
                print("=" * 60)
                print(output)
                session_stats['successful'] += 1
            else:
                print(f"❌ Command failed: {output}")
            
            print()
            
        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            nl_interface.logger.error(f"An unexpected error occurred in the interactive loop: {e}")
            print("❌ An unexpected error occurred. Please check the logs.")

    print("\n👋 Goodbye!")


def show_interactive_help():
    """Show interactive help examples."""
    print("\n💡 Natural Language Command Examples:")
    print("=" * 50)
    
    examples = [
        ("Basic queries", [
            "get firewall policies from host gw1",
            "show interfaces from 192.168.1.1", 
            "list vpn tunnels from host fw1"
        ]),
        ("With intelligent formatting", [
            "get firewall policies from host gw1 and provide a summary",
            "show interfaces from 192.168.1.1 in table format",
            "list address objects from host fw1 as json"
        ]),
        ("With smart filtering", [
            "get firewall policies from host gw1 show only enabled",
            "list interfaces from 192.168.1.1 sort by name", 
            "show vpn status from host fw1 filter by active"
        ]),
        ("Advanced queries", [
            "find disabled firewall rules from host gw1",
            "show system performance from 192.168.1.1 as summary",
            "get top 10 sessions from host fw1 group by destination"
        ]),
        ("Special commands", [
            "hosts - show configured hosts",
            "help - show this help",
            "clear - clear screen",
            "quit - exit interactive mode"
        ])
    ]
    
    for category, cmds in examples:
        print(f"\n--- {category} ---")
        for cmd in cmds:
            print(f"  • {cmd}")
    print()
