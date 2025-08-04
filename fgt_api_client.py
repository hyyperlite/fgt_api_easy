#!/usr/bimport argparse
import json
import sys
import configparser
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import warnings

# Disable SSL warnings by default unless explicitly enabled
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from pyFGT.fortigate import FortiGate
    from pyFGT.fortigate import FGTBaseException, FGTValidSessionException, FGTValueError
    from pyFGT.fortigate import FGTResponseNotFormedCorrect, FGTConnectionError, FGTConnectTimeout
except ImportError:
    print("Error: pyfgt package not found. Please install it using: pip install pyfgt")
    sys.exit(1)
"""
FortiGate API Client

A simple command-line interface for interacting with FortiGate devices using the pyfgt library.
Supports authentication via API key or username/password, and can read configuration from a file.
"""

import argparse
import json
import sys
import configparser
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

try:
    from pyFGT.fortigate import FortiGate
    from pyFGT.fortigate import FGTBaseException, FGTValidSessionException, FGTValueError
    from pyFGT.fortigate import FGTResponseNotFormedCorrect, FGTConnectionError, FGTConnectTimeout
except ImportError:
    print("Error: pyfgt package not found. Please install it using: pip install git+https://github.com/p4r4n0y1ng/pyfgt.git")
    sys.exit(1)


class FortiGateAPIClient:
    """FortiGate API Client wrapper class"""
    
    def __init__(self, host: str, username: str = None, password: str = None, 
                 apikey: str = None, use_ssl: bool = True, verify_ssl: bool = False,
                 timeout: int = 300, debug: bool = False):
        """
        Initialize the FortiGate API client
        
        Args:
            host: FortiGate IP address or hostname
            username: Username for authentication (required even with API key)
            password: Password for authentication
            apikey: API key for authentication (alternative to password)
            use_ssl: Whether to use HTTPS (default: True)
            verify_ssl: Whether to verify SSL certificates (default: False)
            timeout: Request timeout in seconds (default: 300)
            debug: Enable debug mode (default: False)
        """
        self.host = host
        self.username = username or "admin"
        self.password = password
        self.apikey = apikey
        self.use_ssl = use_ssl
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.debug = debug
        
        # Validate authentication parameters
        if not apikey and not password:
            raise ValueError("Either password or apikey must be provided")
    
    def _create_connection(self) -> FortiGate:
        """Create and return a FortiGate connection object"""
        kwargs = {
            'debug': self.debug,
            'use_ssl': self.use_ssl,
            'verify_ssl': self.verify_ssl,
            'timeout': self.timeout
        }
        
        if self.apikey:
            kwargs['apikey'] = self.apikey
            return FortiGate(self.host, self.username, **kwargs)
        else:
            return FortiGate(self.host, self.username, self.password, **kwargs)
    
    def execute_request(self, method: str, endpoint: str, data: Dict[str, Any] = None,
                       query_params: list = None) -> Tuple[int, Dict[str, Any]]:
        """
        Execute a request to the FortiGate API
        
        Args:
            method: HTTP method (get, post, put, delete)
            endpoint: API endpoint path
            data: Request body data (for POST/PUT requests)
            query_params: List of query parameters (e.g., ["vdom=root", "format=name"])
            
        Returns:
            Tuple of (status_code, response_data)
        """
        method = method.lower()
        if method not in ['get', 'post', 'put', 'delete']:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Ensure endpoint starts with /
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        
        try:
            with self._create_connection() as fgt:
                # Prepare arguments
                args = query_params or []
                kwargs = data or {}
                
                # Execute the request based on method
                if method == 'get':
                    return fgt.get(endpoint, *args)
                elif method == 'post':
                    return fgt.post(endpoint, *args, **kwargs)
                elif method == 'put':
                    return fgt.put(endpoint, *args, **kwargs)
                elif method == 'delete':
                    return fgt.delete(endpoint, *args)
                    
        except (FGTConnectionError, FGTConnectTimeout) as e:
            print(f"Connection error: {e}")
            return -1, {"error": "Connection failed", "details": str(e)}
        except FGTValidSessionException as e:
            print(f"Session error: {e}")
            return -2, {"error": "Invalid session", "details": str(e)}
        except FGTBaseException as e:
            print(f"FortiGate API error: {e}")
            return -3, {"error": "API error", "details": str(e)}
        except Exception as e:
            print(f"Unexpected error: {e}")
            return -4, {"error": "Unexpected error", "details": str(e)}


def load_config_file(config_path: str) -> Dict[str, str]:
    """
    Load configuration from a file (supports INI and JSON formats)
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing configuration parameters
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    config = {}
    
    # Try to load as JSON first
    try:
        with open(config_file, 'r') as f:
            json_config = json.load(f)
            # Flatten nested structure if needed
            if 'fortigate' in json_config:
                config = json_config['fortigate']
            else:
                config = json_config
        return config
    except json.JSONDecodeError:
        pass
    
    # Try to load as INI file
    try:
        parser = configparser.ConfigParser()
        parser.read(config_file)
        
        # Use [fortigate] section if available, otherwise use [DEFAULT]
        section = 'fortigate' if 'fortigate' in parser else 'DEFAULT'
        config = dict(parser[section])
        return config
    except Exception as e:
        raise ValueError(f"Unable to parse configuration file: {e}")


def parse_data_argument(data_str: str) -> Dict[str, Any]:
    """
    Parse data argument from command line (JSON string)
    
    Args:
        data_str: JSON string containing request data
        
    Returns:
        Dictionary containing parsed data
    """
    try:
        return json.loads(data_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON data: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="FortiGate API Client - Simple CLI for FortiGate REST API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get all address objects using API key
  %(prog)s -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/address

  # Get address objects in specific VDOM with filter
  %(prog)s -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/address -q 'vdom=root' -q 'format=name'

  # Create an address object using JSON data  
  %(prog)s -i 192.168.1.99 -k your_api_key -m post -e /cmdb/firewall/address -d '{"name": "test_host", "subnet": "10.1.1.1/32"}'

  # Use configuration file
  %(prog)s -c config.ini -m get -e /cmdb/firewall/address

  # Disable pretty printing for compact output
  %(prog)s -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/address --no-pretty

  # Enable SSL warnings (disabled by default)
  %(prog)s -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/address --ssl-warnings

Configuration file format (INI):
  [fortigate]
  host = 192.168.1.99
  apikey = your_api_key_here
  # or use username/password:
  # username = admin
  # password = your_password

Configuration file format (JSON):
  {
    "fortigate": {
      "host": "192.168.1.99",
      "apikey": "your_api_key_here"
    }
  }
        """)
    
    # Connection arguments group
    conn_group = parser.add_argument_group('Connection')
    conn_group.add_argument('-c', '--config', metavar='FILE',
                           help='Configuration file path (INI or JSON format)')
    conn_group.add_argument('-i', '--host', '--ip', metavar='HOST',
                           help='FortiGate IP address or hostname')
    conn_group.add_argument('-u', '--username', metavar='USER', default='admin',
                           help='Username (default: admin)')
    conn_group.add_argument('-p', '--password', metavar='PASS',
                           help='Password for authentication')
    conn_group.add_argument('-k', '--apikey', metavar='KEY',
                           help='API key for authentication')
    
    # Request arguments group
    req_group = parser.add_argument_group('Request')
    req_group.add_argument('-m', '--method', required=True,
                          choices=['get', 'post', 'put', 'delete'],
                          help='HTTP method to use')
    req_group.add_argument('-e', '--endpoint', required=True, metavar='PATH',
                          help='API endpoint path (e.g., /cmdb/firewall/address)')
    req_group.add_argument('-d', '--data', metavar='JSON',
                          help='Request data as JSON string (for POST/PUT)')
    req_group.add_argument('-q', '--query', metavar='PARAM', action='append',
                          help='Query parameters (can be used multiple times)')
    
    # Options group
    opt_group = parser.add_argument_group('Options')
    opt_group.add_argument('--no-ssl', action='store_true',
                          help='Use HTTP instead of HTTPS')
    opt_group.add_argument('--verify-ssl', action='store_true',
                          help='Verify SSL certificates')
    opt_group.add_argument('--ssl-warnings', action='store_true',
                          help='Enable SSL warnings (disabled by default)')
    opt_group.add_argument('--timeout', type=int, default=300, metavar='SEC',
                          help='Request timeout in seconds (default: 300)')
    opt_group.add_argument('--debug', action='store_true',
                          help='Enable debug mode')
    opt_group.add_argument('--no-pretty', action='store_true',
                          help='Disable pretty print JSON output (pretty print is enabled by default)')
    opt_group.add_argument('--pretty', action='store_true',
                          help='Enable pretty print JSON output (default, kept for compatibility)')
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config:
        try:
            config = load_config_file(args.config)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error loading configuration: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Handle SSL warnings - re-enable them if explicitly requested
    if args.ssl_warnings:
        warnings.resetwarnings()
        # Re-enable urllib3 warnings
        import urllib3
        urllib3.warnings.simplefilter('default', urllib3.exceptions.InsecureRequestWarning)
    
    # Determine connection parameters (command line overrides config file)
    host = args.host or config.get('host') or config.get('ip')
    username = args.username or config.get('username', 'admin')
    password = args.password or config.get('password')
    apikey = args.apikey or config.get('apikey')
    
    if not host:
        print("Error: FortiGate host/IP address is required", file=sys.stderr)
        sys.exit(1)
    
    if not apikey and not password:
        print("Error: Either API key or password is required", file=sys.stderr)
        sys.exit(1)
    
    # Parse request data if provided
    request_data = None
    if args.data:
        try:
            request_data = parse_data_argument(args.data)
        except ValueError as e:
            print(f"Error parsing data: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Create client and execute request
    try:
        client = FortiGateAPIClient(
            host=host,
            username=username,
            password=password,
            apikey=apikey,
            use_ssl=not args.no_ssl,
            verify_ssl=args.verify_ssl,
            timeout=args.timeout,
            debug=args.debug
        )
        
        status_code, response = client.execute_request(
            method=args.method,
            endpoint=args.endpoint,
            data=request_data,
            query_params=args.query
        )
        
        # Output results
        print(f"Status Code: {status_code}")
        
        # Pretty print is the default unless --no-pretty is specified
        use_pretty = not args.no_pretty
        
        if use_pretty:
            print("Response:")
            print(json.dumps(response, indent=2, default=str))
        else:
            print(f"Response: {response}")
        
        # Exit with non-zero code for errors
        if status_code < 0:
            sys.exit(1)
        elif status_code >= 400:
            sys.exit(2)
            
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)


if __name__ == '__main__':
    main()
