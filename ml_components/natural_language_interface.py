#!/usr/bin/env python3
"""
Natural Language Interface for FortiGate API Client

Provides intelligent parsing of natural language commands into structured API calls.
"""

import re
import os
import json
import glob
import logging
import readline
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import configparser
from pathlib import Path

# Import the new AI formatter and enhanced ML intent classifier
try:
    from .ai_formatter import format_with_ai, AIDataFormatter
    from .enhanced_intent_classifier import EnhancedMLIntentClassifier, get_enhanced_intent_classifier
    ENHANCED_ML_AVAILABLE = True
except ImportError:
    # Fallback to original intent classifier if enhanced not available
    try:
        from .intent_classifier import classify_user_intent, MLIntentClassifier
        ENHANCED_ML_AVAILABLE = False
    except ImportError:
        # Ultimate fallback if no ML available
        def classify_user_intent(query, endpoint=None):
            return None
        ENHANCED_ML_AVAILABLE = False
        MLIntentClassifier = None

# Fallback if AI formatter not available
try:
    from .ai_formatter import format_with_ai, AIDataFormatter
except ImportError:
    def format_with_ai(data, user_query, endpoint=None):
        return str(data)
    AIDataFormatter = None


@dataclass
class ParsedCommand:
    """Parsed natural language command structure"""
    method: str
    endpoint: str
    host: Optional[str] = None
    format: str = 'auto'
    query: Optional[str] = None
    host_config: Optional[Dict] = None
    confidence: float = 0.0
    original_command: str = ""


class NaturalLanguageInterface:
    """Natural language parser for FortiGate API commands"""
    
    def __init__(self, host_files: Optional[List[str]] = None):
        """Initialize the natural language interface
        
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
            self.logger.setLevel(logging.WARNING)  # Only show warnings and errors by default
        
        self.hosts = self._load_host_configs()
        
        # Method detection patterns with confidence scoring
        self.method_patterns = {
            'get': {
                'high': ['get', 'show', 'list', 'display', 'retrieve', 'fetch', 'view'],
                'medium': ['find', 'search', 'check', 'see'],
                'low': ['what', 'which', 'how many']
            },
            'post': {
                'high': ['create', 'add', 'new', 'make', 'insert'],
                'medium': ['configure', 'setup', 'build'],
                'low': ['enable']
            },
            'put': {
                'high': ['update', 'modify', 'change', 'edit', 'alter'],
                'medium': ['set', 'configure', 'adjust'],
                'low': ['fix', 'correct']
            },
            'delete': {
                'high': ['delete', 'remove', 'del', 'destroy'],
                'medium': ['disable', 'turn off'],
                'low': ['stop']
            }
        }
        
        # Comprehensive endpoint mapping with aliases
        self.endpoint_patterns = {
            '/cmdb/firewall/policy': {
                'aliases': ['firewall policy', 'policies', 'fw policy', 'rules', 'firewall rules', 'security policy'],
                'keywords': ['policy', 'rule', 'firewall', 'security']
            },
            '/cmdb/firewall/address': {
                'aliases': ['address object', 'addresses', 'address', 'ip address', 'host address'],
                'keywords': ['address', 'host', 'ip', 'subnet']
            },
            '/cmdb/system/interface': {
                'aliases': ['interface', 'interfaces', 'ports', 'network interface', 'system interface', 'network ports'],
                'keywords': ['interface', 'port', 'network', 'ethernet', 'system']
            },
            '/cmdb/firewall/service': {
                'aliases': ['service object', 'services', 'service', 'port service', 'protocol service'],
                'keywords': ['service', 'protocol', 'tcp', 'udp']
            },
            '/cmdb/vpn/ipsec/phase1-interface': {
                'aliases': ['vpn', 'ipsec', 'tunnel', 'vpn tunnel', 'phase1'],
                'keywords': ['vpn', 'ipsec', 'tunnel', 'phase1']
            },
            '/cmdb/user/local': {
                'aliases': ['local user', 'users', 'user account', 'account'],
                'keywords': ['user', 'account', 'local', 'authentication']
            },
            '/monitor/system/performance': {
                'aliases': ['performance', 'system stats', 'cpu', 'memory', 'system performance'],
                'keywords': ['performance', 'cpu', 'memory', 'stats', 'system']
            },
            '/monitor/firewall/session': {
                'aliases': ['sessions', 'connections', 'active sessions', 'traffic'],
                'keywords': ['session', 'connection', 'traffic', 'active']
            },
            '/monitor/vpn/ipsec': {
                'aliases': ['vpn status', 'tunnel status', 'vpn monitor', 'ipsec status'],
                'keywords': ['vpn status', 'tunnel status', 'monitor']
            },
            '/cmdb/system/global': {
                'aliases': ['system config', 'global config', 'system settings'],
                'keywords': ['system', 'global', 'config', 'settings']
            },
            '/cmdb/antivirus/profile': {
                'aliases': ['antivirus', 'av profile', 'virus protection'],
                'keywords': ['antivirus', 'av', 'virus', 'security']
            },
            '/cmdb/ips/sensor': {
                'aliases': ['ips', 'intrusion prevention', 'ips sensor'],
                'keywords': ['ips', 'intrusion', 'sensor', 'security']
            }
        }
        
        # Format detection patterns
        self.format_patterns = {
            'csv': ['csv', 'comma separated', 'comma-separated', 'spreadsheet'],
            'tsv': ['tsv', 'tab separated', 'tab-separated'],
            'html': ['html', 'web page', 'webpage', 'browser'],
            'json': ['json', 'raw', 'full data', 'complete', 'detailed'],
            'summary': ['summary', 'overview', 'brief', 'short', 'condensed'],
            'table': ['table', 'tabular', 'columns', 'rows', 'formatted', 'put in table', 'table format', 'in table format'],
            'tree': ['tree', 'hierarchy', 'nested', 'structured'],
            'list': ['list', 'bullet', 'enumerate', 'items']
        }
        
        # Query intent patterns
        self.query_patterns = {
            'filter': {
                'patterns': [
                    r'show only (\w+)',
                    r'only (\w+)',
                    r'filter by (\w+)',
                    r'where (\w+)',
                    r'with (\w+)',
                    r'enabled only',
                    r'disabled only',
                    r'active only'
                ]
            },
            'sort': {
                'patterns': [
                    r'sort by (\w+)',
                    r'order by (\w+)',
                    r'sorted by (\w+)',
                    r'ascending',
                    r'descending'
                ]
            },
            'group': {
                'patterns': [
                    r'group by (\w+)',
                    r'grouped by (\w+)',
                    r'organize by (\w+)'
                ]
            },
            'limit': {
                'patterns': [
                    r'top (\d+)',
                    r'first (\d+)',
                    r'limit (\d+)',
                    r'show (\d+)'
                ]
            }
        }
    
    def _load_host_configs(self) -> Dict[str, Dict]:
        """Load host configurations from specified files/directories or default config directory"""
        hosts = {}
        
        if self.host_files:
            # Use only the specified host files/directories
            found_configs = []
            
            for host_file in self.host_files:
                if os.path.isdir(host_file):
                    # If it's a directory, search for config files in it
                    config_patterns = ['*.json', '*.ini']
                    for pattern in config_patterns:
                        search_path = os.path.join(host_file, pattern)
                        found_files = glob.glob(search_path)
                        found_configs.extend(found_files)
                elif os.path.isfile(host_file):
                    # If it's a file, add it directly
                    found_configs.append(host_file)
                else:
                    self.logger.warning(f"Host file/directory not found: {host_file}")
        else:
            # Default behavior - search in default config directory only
            search_dirs = ['./config']
            config_patterns = ['*.json', '*.ini']
            found_configs = []
            
            for search_dir in search_dirs:
                if os.path.exists(search_dir):
                    for pattern in config_patterns:
                        search_path = os.path.join(search_dir, pattern)
                        found_files = glob.glob(search_path)
                        found_configs.extend(found_files)
        
        # Process each config file found
        for config_file in set(found_configs):  # Remove duplicates
            try:
                hosts_from_file = self._parse_config_file(config_file)
                if hosts_from_file:
                    hosts.update(hosts_from_file)
                    self.logger.debug(f"Loaded {len(hosts_from_file)} host(s) from {config_file}")
            except Exception as e:
                self.logger.debug(f"Could not parse {config_file}: {e}")
        
        if hosts:
            self.logger.info(f"Found {len(hosts)} host configuration(s) from config files")
        else:
            if self.host_files:
                self.logger.info("No host configurations found in specified files/directories")
            else:
                self.logger.info("No host configurations found in default config directory (./config)")
        
        return hosts
    
    def _parse_config_file(self, config_file: str) -> Dict[str, Dict]:
        """Parse a config file and extract valid host configurations"""
        hosts = {}
        file_ext = os.path.splitext(config_file)[1].lower()
        
        try:
            if file_ext == '.json':
                hosts = self._parse_json_config(config_file)
            elif file_ext == '.ini':
                hosts = self._parse_ini_config(config_file)
            else:
                # Try both formats
                try:
                    hosts = self._parse_json_config(config_file)
                except:
                    hosts = self._parse_ini_config(config_file)
                    
        except Exception as e:
            self.logger.debug(f"Failed to parse {config_file}: {e}")
        
        # Filter and normalize valid host configs
        valid_hosts = {}
        for name, config in hosts.items():
            if self._is_valid_host_config(name, config):
                # Normalize the config to standard format
                normalized_config = self._normalize_host_config(name, config)
                valid_hosts[name] = normalized_config
            else:
                self.logger.debug(f"Skipping invalid host config '{name}' in {config_file}")
        
        return valid_hosts
    
    def _parse_json_config(self, config_file: str) -> Dict[str, Dict]:
        """Parse JSON config file"""
        with open(config_file, 'r') as f:
            data = json.load(f)
        
        hosts = {}
        
        # Handle different JSON structures
        if 'hosts' in data:
            hosts = data['hosts']
        elif isinstance(data, dict):
            # Check if this looks like a direct host config
            if any(key in data for key in ['ip', 'host', 'apikey', 'api_key']):
                # Single host config
                name = data.get('name', os.path.splitext(os.path.basename(config_file))[0])
                hosts[name] = data
            else:
                # Assume each top-level key is a host name
                hosts = data
        
        return hosts
    
    def _parse_ini_config(self, config_file: str) -> Dict[str, Dict]:
        """Parse INI config file"""
        config = configparser.ConfigParser()
        config.read(config_file)
        
        hosts = {}
        
        for section_name in config.sections():
            section = dict(config[section_name])
            hosts[section_name] = section
        
        return hosts
    
    def _is_valid_host_config(self, name: str, config: Dict) -> bool:
        """Check if host config has required fields: name, ip/host, apikey"""
        if not isinstance(config, dict):
            return False
        
        # Must have IP or host
        has_ip = any(key in config for key in ['ip', 'host', 'hostname', 'address'])
        
        # Must have API key  
        has_apikey = any(key in config for key in ['apikey', 'api_key', 'key', 'token'])
        
        # Must have a name (either in config or as section name)
        has_name = name or config.get('name')
        
        return has_ip and has_apikey and has_name
    
    def _normalize_host_config(self, name: str, config: Dict) -> Dict:
        """Normalize host config to standard format"""
        normalized = {
            'name': name,
            'ip': None,
            'apikey': None
        }
        
        # Extract IP/host
        for ip_key in ['ip', 'host', 'hostname', 'address']:
            if ip_key in config:
                normalized['ip'] = config[ip_key]
                break
        
        # Extract API key
        for key_field in ['apikey', 'api_key', 'key', 'token']:
            if key_field in config:
                normalized['apikey'] = config[key_field]
                break
        
        # Copy additional fields that might be useful
        for field in ['port', 'timeout', 'verify_ssl', 'vdom']:
            if field in config:
                normalized[field] = config[field]
        
        return normalized
    
    def parse_natural_command(self, command: str) -> ParsedCommand:
        """Parse a natural language command into structured parameters"""
        command = command.strip()
        command_lower = command.lower()
        
        # First attempt: Use enhanced ML intent classifier if available
        if ENHANCED_ML_AVAILABLE:
            ml_result = self._parse_with_enhanced_ml(command, command_lower)
            if ml_result and ml_result.confidence > 0.7:
                return ml_result
        
        # Fallback: Use traditional pattern matching with confidence scoring
        method, method_conf = self._extract_method(command_lower)
        endpoint, endpoint_conf = self._extract_endpoint(command_lower)
        host, host_config, host_conf = self._extract_host(command_lower)
        # In pure AI mode, don't extract format or query - let AI handle everything
        
        # Calculate overall confidence (only method, endpoint, host)
        confidence = (method_conf + endpoint_conf + host_conf) / 3.0
        
        return ParsedCommand(
            method=method,
            endpoint=endpoint,
            host=host,
            format='auto',  # Always auto - AI will determine format from natural language
            query=None,     # No query parameters - AI handles filtering/fields from request
            host_config=host_config,
            confidence=confidence,
            original_command=command
        )
    
    def _parse_with_enhanced_ml(self, command: str, command_lower: str) -> Optional[ParsedCommand]:
        """Parse command using enhanced ML intent classifier"""
        try:
            # Extract basic components first
            method, method_conf = self._extract_method(command_lower)
            endpoint, endpoint_conf = self._extract_endpoint(command_lower)
            host, host_config, host_conf = self._extract_host(command_lower)
            
            # Use enhanced ML classifier for intent understanding, but don't extract format
            # In pure AI mode, the AI formatter will interpret the natural language directly
            classifier = get_enhanced_intent_classifier()
            intent = classifier.classify_intent(command, endpoint)
            
            if intent:
                # In pure AI mode, don't extract format or build query parameters
                # Calculate confidence based on intent understanding
                ml_confidence = (intent.field_confidence + intent.filter_confidence) / 2.0
                overall_confidence = (method_conf + endpoint_conf + host_conf + ml_confidence) / 4.0
                
                # Only return ML result if confidence is reasonable
                if overall_confidence > 0.5:
                    return ParsedCommand(
                        method=method,
                        endpoint=endpoint,
                        host=host,
                        format='auto',  # Always auto - AI determines format from natural language
                        query=None,     # No query parameters - AI handles everything
                        host_config=host_config,
                        confidence=overall_confidence,
                        original_command=command
                    )
            
        except Exception as e:
            self.logger.warning(f"Enhanced ML parsing failed: {e}")
        
        return None
    
    def _extract_method(self, command: str) -> Tuple[str, float]:
        """Extract HTTP method from command with confidence"""
        best_method = 'get'
        best_confidence = 0.5  # Default confidence for get
        
        for method, pattern_groups in self.method_patterns.items():
            for confidence_level, patterns in pattern_groups.items():
                for pattern in patterns:
                    if pattern in command:
                        conf_score = {'high': 1.0, 'medium': 0.7, 'low': 0.4}[confidence_level]
                        if conf_score > best_confidence:
                            best_method = method
                            best_confidence = conf_score
        
        return best_method, best_confidence
    
    def _extract_endpoint(self, command: str) -> Tuple[str, float]:
        """Extract API endpoint from command with confidence"""
        best_endpoint = '/cmdb/firewall/policy'  # Default
        best_confidence = 0.3
        
        for endpoint, config in self.endpoint_patterns.items():
            confidence = 0.0
            
            # Check aliases (high confidence)
            for alias in config['aliases']:
                if alias in command:
                    confidence = max(confidence, 0.9)
            
            # Check keywords (medium confidence)
            keyword_matches = sum(1 for keyword in config['keywords'] if keyword in command)
            if keyword_matches > 0:
                confidence = max(confidence, 0.6 + (keyword_matches * 0.1))
            
            if confidence > best_confidence:
                best_endpoint = endpoint
                best_confidence = confidence
        
        # Check for explicit endpoint paths
        endpoint_match = re.search(r'(/(?:cmdb|monitor|api)/[\w/\-]+)', command)
        if endpoint_match:
            return endpoint_match.group(1), 1.0
        
        return best_endpoint, best_confidence
    
    def _extract_host(self, command: str) -> Tuple[Optional[str], Optional[Dict], float]:
        """Extract host information from command"""
        # Look for 'from host X' pattern
        host_match = re.search(r'from host (\w+)', command)
        if host_match:
            host_name = host_match.group(1)
            if host_name in self.hosts:
                # Hosts are already normalized when loaded
                host_config = self.hosts[host_name]
                return host_name, host_config, 1.0
            else:
                # Unknown host - will need to be configured or found
                return host_name, None, 0.8
        
        # Look for 'from X' pattern where X is a known host name (more flexible)
        from_match = re.search(r'from (\w+)', command)
        if from_match:
            potential_host = from_match.group(1)
            if potential_host in self.hosts:
                host_config = self.hosts[potential_host]
                return potential_host, host_config, 0.9
        
        # Look for IP address pattern  
        ip_match = re.search(r'from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', command)
        if ip_match:
            ip = ip_match.group(1)
            # Check if this IP exists in our configs
            for name, config in self.hosts.items():
                if config['ip'] == ip:
                    return name, config, 1.0
            # Unknown IP
            return ip, {'name': ip, 'ip': ip, 'apikey': None}, 0.5
        
        # Look for hostname patterns
        hostname_match = re.search(r'from (\w+\.\w+)', command)
        if hostname_match:
            hostname = hostname_match.group(1)
            # Check if this hostname exists in configs
            for name, config in self.hosts.items():
                if config['ip'] == hostname:
                    return name, config, 1.0
            return hostname, {'name': hostname, 'ip': hostname, 'apikey': None}, 0.5
        
        # No specific host mentioned - don't assume a default
        return None, None, 0.0
    
    def _extract_format(self, command: str) -> Tuple[str, float]:
        """Extract desired output format from command"""
        command_lower = command.lower()
        best_format = 'auto'
        best_confidence = 0.5
        
        # Enhanced format detection patterns
        format_detection_patterns = {
            'csv': [
                r'\bcsv\b', r'\bcomma.?separated\b', r'\bspreadsheet\b',
                r'\bas csv\b', r'\bin csv\b', r'\bformat.{0,10}csv\b', r'\bcsv.{0,10}format\b'
            ],
            'tsv': [
                r'\btsv\b', r'\btab.?separated\b',
                r'\bas tsv\b', r'\bin tsv\b', r'\bformat.{0,10}tsv\b'
            ],
            'html': [
                r'\bhtml\b', r'\bweb.?page\b', r'\bbrowser\b',
                r'\bas html\b', r'\bin html\b', r'\bhtml.{0,10}table\b'
            ],
            'json': [
                r'\bjson\b', r'\braw\b', r'\bfull.data\b',
                r'\bas json\b', r'\bin json\b', r'\bjson.{0,10}format\b'
            ],
            'summary': [
                r'\bsummary\b', r'\boverview\b', r'\bbrief\b', r'\bshort\b',
                r'\bcondensed\b', r'\bsummarize\b'
            ],
            'table': [
                r'\btable\b', r'\btabular\b', r'\bcolumns?\b', r'\brows?\b',
                r'\bas.{0,5}table\b', r'\btable.{0,10}format\b'
            ],
            'list': [
                r'\blist\b', r'\bbullet\b', r'\benumerate\b', r'\bitems?\b',
                r'\bas.{0,5}list\b', r'\blist.{0,10}format\b'
            ]
        }
        
        # Check for explicit format patterns with regex for better matching
        for format_type, patterns in format_detection_patterns.items():
            for pattern in patterns:
                if re.search(pattern, command_lower):
                    return format_type, 0.9
        
        # Fallback to simple word matching
        for format_type, patterns in self.format_patterns.items():
            for pattern in patterns:
                if pattern.lower() in command_lower:
                    return format_type, 0.8
        
        # Contextual format detection
        if any(word in command_lower for word in ['and provide', 'show me', 'give me']):
            if any(word in command_lower for word in ['summary', 'overview']):
                return 'summary', 0.7
        
        return best_format, best_confidence
    
    def _extract_query(self, command: str) -> Tuple[Optional[str], float]:
        """Extract additional query parameters"""
        best_query = None
        best_confidence = 0.0
        
        for intent, config in self.query_patterns.items():
            for pattern in config['patterns']:
                match = re.search(pattern, command)
                if match:
                    best_query = match.group(0)
                    best_confidence = 0.8
                    break
        
        return best_query, best_confidence
    
    def prompt_for_missing_info(self, parsed_cmd: ParsedCommand) -> ParsedCommand:
        """Interactively prompt for missing information (API key only)"""
        if not parsed_cmd.host_config:
            if parsed_cmd.host:
                print(f"\n🔧 Host '{parsed_cmd.host}' not found in configuration.")
                print("💡 Create a config file with this host or provide details now:")
                config = self._prompt_for_host_config(parsed_cmd.host)
                if config:
                    parsed_cmd.host_config = config
            else:
                print(f"\n🔧 No host specified. Available options:")
                if self.hosts:
                    print("Available hosts:", ', '.join(self.hosts.keys()))
                print("Or specify: 'from host <name>' or 'from <ip_address>'")
        
        return parsed_cmd
    
    def _prompt_for_host_config(self, host_name: str) -> Optional[Dict]:
        """Prompt user for host configuration (API key only - no session persistence)"""
        print(f"\n📝 Temporary config for: {host_name}")
        print("⚠️  Note: This will not be saved between sessions for security")
        
        ip = input("IP address: ").strip()
        if not ip:
            print("❌ IP address required")
            return None
        
        print("\n🔐 FortiGate REST API requires API key authentication")
        apikey = input("API Key: ").strip()
        if not apikey:
            print("❌ API key required")
            return None
        
        config = {
            'ip': ip,
            'name': host_name,
            'apikey': apikey
        }
        
        # Add to session only (not persisted)
        self.hosts[host_name] = config
        
        print(f"✅ Host '{host_name}' configured for this session only!")
        print("💡 Create a config file for permanent storage")
        
        return self._normalize_host_config(host_name, config)
        return config
    
    def build_cli_args(self, parsed_cmd: ParsedCommand) -> Dict[str, str]:
        """Build CLI arguments from parsed command"""
        args = {
            'enable_ai': True,
            'method': parsed_cmd.method,
            'endpoint': parsed_cmd.endpoint
        }
        
        if parsed_cmd.host_config:
            args['host'] = parsed_cmd.host_config['ip']
            
            if parsed_cmd.host_config.get('auth_method') == 'apikey':
                args['api_key'] = parsed_cmd.host_config['apikey']
            else:
                args['username'] = parsed_cmd.host_config.get('username')
                args['password'] = parsed_cmd.host_config.get('password')
        
        # In pure AI mode, don't pass format or query parameters
        # The AI will interpret everything from the original command
        
        return args
    
    def execute_parsed_command(self, parsed_cmd: ParsedCommand) -> Tuple[bool, str]:
        """Execute a parsed natural language command using the FortiGate API client
        
        Args:
            parsed_cmd: The parsed command to execute
            
        Returns:
            Tuple of (success, output/error_message)
        """
        try:
            # Import here to avoid circular imports
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from fgt_api_client import FortiGateAPIClient
            
            if not parsed_cmd.host_config:
                return False, "❌ No host configuration available"
            
            # Extract connection parameters (API key only)
            host = parsed_cmd.host_config['ip']
            apikey = parsed_cmd.host_config.get('apikey')
            
            if not apikey:
                return False, "❌ No API key found in host configuration"
            
            # Create client with NO ML processing (we'll do it ourselves with pure AI)
            client = FortiGateAPIClient(
                host=host,
                apikey=apikey,
                use_ssl=True,
                verify_ssl=False,
                timeout=30,
                debug=False,
                enable_ml=False  # Important: disable client ML, we handle it with pure AI
            )
            
            # Make raw API call - get pure JSON data
            print("🔄 Making raw API call...")
            status_code, raw_response = client.execute_request(
                method=parsed_cmd.method,
                endpoint=parsed_cmd.endpoint
            )
            
            if status_code != 200:
                return False, f"❌ API call failed (status {status_code}): {raw_response}"
            
            print(f"✅ Raw data retrieved: {len(raw_response.get('results', []))} records")
            
            # Pass everything to AI for complete processing
            print("🧠 Processing with pure AI...")
            try:
                from ml_components.ai_formatter import AIDataFormatter
                ai_formatter = AIDataFormatter()
                ai_output = ai_formatter.format_with_complete_ai(
                    raw_data=raw_response,
                    user_request=parsed_cmd.original_command,
                    endpoint=parsed_cmd.endpoint
                )
                return True, ai_output
            except Exception as ai_error:
                # Fallback to simple JSON display if AI fails
                import json
                return True, json.dumps(raw_response.get('results', []), indent=2)
                
        except Exception as e:
            return False, f"❌ Error executing command: {e}"

    def build_cli_command(self, parsed_cmd: ParsedCommand) -> str:
        """Build traditional CLI command string from parsed command"""
        cmd_parts = ["python3", "fgt_api_client.py", "--enable-ai"]
        
        # Add host and authentication (API key only)
        if parsed_cmd.host_config:
            cmd_parts.extend(["-i", parsed_cmd.host_config['ip']])
            
            # Only support API key authentication (FortiGate REST API requirement)
            if parsed_cmd.host_config.get('apikey'):
                cmd_parts.extend(["-k", parsed_cmd.host_config['apikey']])
            else:
                # Missing API key - command will fail, but show the structure
                cmd_parts.extend(["-k", "<MISSING_API_KEY>"])
        
        # Add method and endpoint
        cmd_parts.extend(["-m", parsed_cmd.method])
        cmd_parts.extend(["-e", parsed_cmd.endpoint])
        
        # In pure AI mode, don't add format or query parameters
        # The AI will interpret the original command directly
        
        return " ".join(cmd_parts)
    
    def get_interpretation_summary(self, parsed_cmd: ParsedCommand) -> str:
        """Generate a human-readable interpretation summary"""
        summary = f"🤖 Interpretation (confidence: {parsed_cmd.confidence:.1%}):\n"
        summary += f"   Method: {parsed_cmd.method.upper()}\n"
        summary += f"   Endpoint: {parsed_cmd.endpoint}\n"
        
        if parsed_cmd.host:
            summary += f"   Host: {parsed_cmd.host}"
            if parsed_cmd.host_config:
                summary += f" ({parsed_cmd.host_config['ip']})\n"
            else:
                summary += " (needs configuration)\n"
        
        summary += f"   Original Request: \"{parsed_cmd.original_command}\"\n"
        summary += f"   (AI will interpret format and fields from natural language)\n"
        
        if parsed_cmd.query:
            summary += f"   Query: {parsed_cmd.query}\n"
        
        return summary
    
    def list_configured_hosts(self) -> str:
        """List all configured hosts"""
        if not self.hosts:
            return "No hosts configured yet."
        
        result = "🏠 Configured Hosts:\n"
        for host_name, config in self.hosts.items():
            result += f"   📍 {host_name}: {config['ip']} ({config.get('auth_method', 'unknown')})\n"
        
        return result


def setup_interactive_readline():
    """Setup readline for command history and editing"""
    try:
        import readline
        import atexit
        
        # Set up history file
        history_file = os.path.expanduser('~/.fgt_history')
        
        # Load existing history
        if os.path.exists(history_file):
            try:
                readline.read_history_file(history_file)
            except:
                pass  # Ignore errors reading history
        
        # Set history length
        readline.set_history_length(1000)
        
        # Save history on exit
        def save_history():
            try:
                readline.write_history_file(history_file)
            except:
                pass  # Ignore errors writing history
        
        atexit.register(save_history)
        
        # Enable tab completion
        readline.parse_and_bind("tab: complete")
        
        # Enable vi-style editing (optional, can be changed to emacs)
        readline.parse_and_bind("set editing-mode emacs")
        
        return True
        
    except ImportError:
        # readline not available
        return False


def interactive_session(nl_interface: NaturalLanguageInterface, host_files: Optional[List[str]] = None):
    """Run an interactive natural language session
    
    Args:
        nl_interface: The natural language interface instance
        host_files: List of host configuration files or directories (for display only)
    """
    # Setup command history and editing
    has_readline = setup_interactive_readline()
    
    print("🤖 FortiGate API Client - Interactive AI Mode")
    print("=" * 60)
    print("Enter natural language commands or type 'help' for examples.")
    print("Type 'quit' or 'exit' to end the session.")
    if has_readline:
        print("💡 Use ↑/↓ arrows for command history, Ctrl+R for search")
    print()
    
    # Show information about host file sources
    if host_files:
        print(f"📂 Using host configuration files/directories: {', '.join(host_files)}")
    else:
        print("📂 Using default config directory: ./config/")
    
    if nl_interface.hosts:
        print(f"📍 Available hosts ({len(nl_interface.hosts)}): {', '.join(nl_interface.hosts.keys())}")
        print("💡 Tip: Use 'from host <name>' in your commands")
    else:
        print("📝 No hosts found in specified config files/directories.")
        print("💡 Create JSON/INI config files with required fields: name, ip, apikey")
        print("   JSON example: {'hosts': {'gw1': {'ip': '192.168.1.1', 'apikey': 'your_key'}}}")
        print("   INI example:  [gw1]\\n              ip = 192.168.1.1\\n              apikey = your_key")
    print()
    
    session_stats = {'commands': 0, 'successful': 0}
    
    while True:
        try:
            command = input("🔤 fgt> ").strip()
            
            if not command:
                continue
            
            if command.lower() in ['quit', 'exit', 'q']:
                if session_stats['commands'] > 0:
                    success_rate = session_stats['successful'] / session_stats['commands']
                    print(f"\n📊 Session Stats: {session_stats['commands']} commands, {success_rate:.1%} success rate")
                print("👋 Goodbye! (Host configs not persisted for security)")
                break
            
            if command.lower() == 'help':
                show_interactive_help()
                continue
            
            if command.lower() == 'hosts':
                print(nl_interface.list_configured_hosts())
                if not nl_interface.hosts:
                    print("\n💡 Example config file formats:")
                    print("JSON: {'hosts': {'gw1': {'ip': '192.168.1.1', 'apikey': 'your_key'}}}")
                    print("INI:  [gw1]\\n      ip = 192.168.1.1\\n      apikey = your_key")
                    print("💡 To load different host files, restart with --host-files option")
                continue
            
            if command.lower() == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                continue
            
            # Process the natural language command
            session_stats['commands'] += 1
            print(f"\n🤖 Processing: {command}")
            
            try:
                parsed_cmd = nl_interface.parse_natural_command(command)
                
                # Show interpretation
                print(nl_interface.get_interpretation_summary(parsed_cmd))
                
                # Check for missing host configuration
                if not parsed_cmd.host_config:
                    if not parsed_cmd.host:
                        print("❌ No host specified. Use 'from host <name>' or 'from <ip>'")
                        print("💡 Available hosts:", ', '.join(nl_interface.hosts.keys()) if nl_interface.hosts else "None configured")
                        continue
                    else:
                        print(f"❌ Host '{parsed_cmd.host}' not found in configurations")
                        print("💡 To use different host files, restart with --host-files option")
                        continue
                
                if not parsed_cmd.host_config.get('apikey'):
                    print("❌ No API key found for host")
                    print("💡 Ensure your config file includes 'apikey' field")
                    continue
                
                # Ask for confirmation if confidence is low
                if parsed_cmd.confidence < 0.7:
                    confirm = input(f"⚠️  Confidence is {parsed_cmd.confidence:.1%}. Proceed? (y/N): ")
                    if confirm.lower() != 'y':
                        continue
                
                # Execute the command
                print("🔄 Executing API call...")
                success, output = nl_interface.execute_parsed_command(parsed_cmd)
                
                if success:
                    print("✅ Command executed successfully")
                    print("=" * 60)
                    print(output)
                    session_stats['successful'] += 1
                else:
                    print(f"❌ Command failed: {output}")
                    # Show the CLI command for debugging
                    cli_command = nl_interface.build_cli_command(parsed_cmd)
                    print(f"💡 Equivalent CLI: {cli_command.replace(parsed_cmd.host_config.get('apikey', ''), '<API_KEY>')}")
                
            except Exception as e:
                print(f"❌ Error processing command: {e}")
                print("💡 Try 'help' for examples or check your command syntax.")
            
            print()  # Add spacing between commands
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break


def show_interactive_help():
    """Show interactive help examples"""
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
        print(f"\n🎯 {category}:")
        for cmd in cmds:
            print(f"   {cmd}")
    
    print(f"\n📝 Supported FortiGate objects:")
    objects = [
        "firewall policies, rules",
        "address objects, addresses",
        "service objects, services",
        "static routes, routing",
        "interfaces, ports",
        "vpn, ipsec, tunnels", 
        "users, authentication",
        "system performance, stats",
        "sessions, connections"
    ]
    for obj in objects:
        print(f"   • {obj}")


if __name__ == "__main__":
    # Test the natural language interface
    nl_interface = NaturalLanguageInterface()
    
    test_commands = [
        "get firewall policies from host gw1 and provide a summary",
        "show interfaces from 192.168.1.1 in table format",
        "list vpn tunnels from host fw1",
        "find disabled policies from host gw2"
    ]
    
    print("🤖 Natural Language Interface Test")
    print("=" * 50)
    
    for cmd in test_commands:
        print(f"\n📝 Testing: {cmd}")
        parsed = nl_interface.parse_natural_command(cmd)
        print(nl_interface.get_interpretation_summary(parsed))
        print(f"💻 CLI: {nl_interface.build_cli_command(parsed)}")
