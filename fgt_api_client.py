#!/usr/bin/env python3
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
from typing import Dict, Any, Tuple, Optional, List, Union
import warnings
import os

# Disable SSL warnings by default unless explicitly enabled
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from pyFGT.fortigate import FortiGate
    from pyFGT.fortigate import FGTBaseException, FGTValidSessionException, FGTValueError
    from pyFGT.fortigate import FGTResponseNotFormedCorrect, FGTConnectionError, FGTConnectTimeout
except ImportError:
    print("Error: pyfgt package not found. Please install it using: pip install git+https://github.com/p4r4n0y1ng/pyfgt.git")
    sys.exit(1)

try:
    from tabulate import tabulate
except ImportError:
    print("Error: tabulate package not found. Please install it using: pip install tabulate")
    sys.exit(1)


class TableFormatter:
    """Handles formatting of FortiGate API responses as tables"""
    
    # Predefined field mappings for common FortiGate objects
    ENDPOINT_FIELD_MAPPINGS = {
        '/cmdb/firewall/address': ['name', 'subnet', 'type', 'comment'],
        '/cmdb/firewall/addrgrp': ['name', 'member', 'comment'],
        '/cmdb/firewall/policy': ['policyid', 'name', 'srcintf', 'dstintf', 'srcaddr', 'dstaddr', 'action', 'status'],
        '/cmdb/firewall/service/custom': ['name', 'protocol', 'tcp-portrange', 'udp-portrange', 'comment'],
        '/cmdb/firewall/service/group': ['name', 'member', 'comment'],
        '/cmdb/system/interface': ['name', 'ip', 'status', 'type', 'vdom'],
        '/cmdb/router/static': ['dst', 'gateway', 'device', 'distance'],
        '/cmdb/user/local': ['name', 'status', 'type'],
        '/monitor/system/status': ['hostname', 'model', 'version', 'serial'],
        '/monitor/system/interface': ['name', 'rx_bytes', 'tx_bytes', 'status'],
        '/monitor/router/ipv4': ['ip_dst', 'gateway', 'interface', 'distance'],
    }
    
    @staticmethod
    def _flatten_value(value: Any) -> str:
        """Convert complex values to simple string representation"""
        if value is None:
            return "-"
        elif isinstance(value, (list, tuple)):
            if not value:
                return "-"
            # Handle list of objects with 'name' field
            if isinstance(value[0], dict) and 'name' in value[0]:
                return ", ".join([item['name'] for item in value if 'name' in item])
            # Handle simple list
            return ", ".join([str(item) for item in value])
        elif isinstance(value, dict):
            # For dictionaries, try to get a meaningful representation
            if 'name' in value:
                return value['name']
            elif len(value) == 1:
                return str(list(value.values())[0])
            else:
                return str(value)
        else:
            return str(value)
    
    @staticmethod
    def _detect_fields(data: List[Dict[str, Any]], endpoint: Optional[str] = None, max_fields: int = 6) -> List[str]:
        """Auto-detect the most relevant fields from the data"""
        if not data:
            return []
        
        # Try predefined mapping first
        if endpoint:
            for pattern, fields in TableFormatter.ENDPOINT_FIELD_MAPPINGS.items():
                if pattern in endpoint:
                    # Return only fields that exist in the data
                    available_fields = []
                    for field in fields:
                        if any(field in item for item in data):
                            available_fields.append(field)
                    if available_fields:
                        return available_fields[:max_fields]
        
        # Fallback: use most common fields from actual data
        field_counts = {}
        for item in data[:10]:  # Sample first 10 items
            for key in item.keys():
                field_counts[key] = field_counts.get(key, 0) + 1
        
        # Sort by frequency and take top fields
        common_fields = sorted(field_counts.items(), key=lambda x: x[1], reverse=True)
        return [field[0] for field in common_fields[:max_fields]]
    
    @staticmethod
    def format_table(response_data: Dict[str, Any], endpoint: Optional[str] = None, 
                    custom_fields: Optional[List[str]] = None, max_width: Optional[int] = None) -> str:
        """
        Format API response data as a table
        
        Args:
            response_data: The API response data
            endpoint: The API endpoint (used for field detection)
            custom_fields: Specific fields to include in the table
            max_width: Maximum width for cell content (truncate if longer)
            
        Returns:
            Formatted table string
        """
        # Handle non-list responses
        if not isinstance(response_data, dict):
            return f"Table format not supported for response type: {type(response_data)}"
        
        # Special handling for monitoring endpoints with time-series data
        if endpoint and '/monitor/' in endpoint and 'results' in response_data:
            return TableFormatter._format_monitoring_table(response_data, endpoint, max_width)
        
        # Extract the actual data list
        data_list = None
        if 'results' in response_data:
            data_list = response_data['results']
        elif isinstance(response_data.get('data'), list):
            data_list = response_data['data']
        elif isinstance(response_data, list):
            data_list = response_data
        else:
            # Single object response - convert to list
            data_list = [response_data]
        
        if not data_list:
            return "No data to display in table format"
        
        # Determine fields to display
        if custom_fields:
            fields = custom_fields
        else:
            fields = TableFormatter._detect_fields(data_list, endpoint)
        
        if not fields:
            return "No suitable fields found for table display"
        
        # Prepare table data
        headers = fields
        rows = []
        
        for item in data_list:
            row = []
            for field in fields:
                value = item.get(field, "-")
                formatted_value = TableFormatter._flatten_value(value)
                
                # Truncate if max_width specified
                if max_width and len(formatted_value) > max_width:
                    formatted_value = formatted_value[:max_width-3] + "..."
                
                row.append(formatted_value)
            rows.append(row)
        
        # Generate table
        table = tabulate(rows, headers=headers, tablefmt="grid", stralign="left")
        
        # Add summary info
        summary = f"\n{len(data_list)} result(s) found"
        if endpoint:
            summary = f"FortiGate API: {endpoint} ({len(data_list)} result(s))"
        
        return f"{summary}\n{table}"
    
    @staticmethod
    def _format_monitoring_table(response_data: Dict[str, Any], endpoint: Optional[str] = None, 
                                max_width: Optional[int] = None) -> str:
        """
        Format monitoring endpoint responses (time-series data) as separate tables per metric
        
        Args:
            response_data: The API response data with time-series structure
            endpoint: The API endpoint 
            max_width: Maximum width for cell content
            
        Returns:
            Formatted table string with separate tables for each metric
        """
        results = response_data.get('results', {})
        
        if not results:
            return "No monitoring data to display"
        
        # First, determine what time periods are available across all metrics
        time_periods = set()
        for metric_name, metric_data in results.items():
            if isinstance(metric_data, list) and len(metric_data) > 0:
                historical = metric_data[0].get('historical', {})
                time_periods.update(historical.keys())
        
        # Sort time periods in logical order (shortest to longest)
        period_order = ['1-min', '10-min', '30-min', '1-hour', '12-hour', '24-hour']
        available_periods = [p for p in period_order if p in time_periods]
        
        # Build separate table for each metric
        tables = []
        
        # Add header with endpoint info
        summary = f"System Resource Usage - Detailed Statistics"
        if endpoint:
            summary = f"FortiGate API: {endpoint} - Detailed Statistics"
        tables.append(summary)
        tables.append("=" * len(summary))
        
        for metric_name, metric_data in results.items():
            if isinstance(metric_data, list) and len(metric_data) > 0:
                metric_info = metric_data[0]
                current_value = metric_info.get('current', 'N/A')
                historical = metric_info.get('historical', {})
                
                # Format the metric name (make it more readable)
                formatted_name = metric_name.replace('_', ' ').title()
                
                # Create individual table for this metric
                headers = ['Time Period', 'Min', 'Max', 'Average']
                rows = []
                
                # Add current value as first row
                formatted_current = TableFormatter._format_metric_value(current_value, metric_name, max_width)
                rows.append(['Current', formatted_current, formatted_current, formatted_current])
                
                # Add statistics for each time period
                for period in available_periods:
                    period_data = historical.get(period, {})
                    
                    min_val = period_data.get('min', '-')
                    max_val = period_data.get('max', '-')
                    avg_val = period_data.get('average', '-')
                    
                    # Format each statistical value
                    formatted_min = TableFormatter._format_metric_value(min_val, metric_name, max_width)
                    formatted_max = TableFormatter._format_metric_value(max_val, metric_name, max_width)
                    formatted_avg = TableFormatter._format_metric_value(avg_val, metric_name, max_width)
                    
                    rows.append([period, formatted_min, formatted_max, formatted_avg])
                
                # Generate table for this metric
                table = tabulate(rows, headers=headers, tablefmt="grid", stralign="left")
                
                # Add metric name and table
                tables.append(f"\n{formatted_name}:")
                tables.append(table)
        
        return "\n".join(tables)
    
    @staticmethod
    def _format_metric_value(value: Any, metric_name: str, max_width: Optional[int] = None) -> str:
        """
        Format a metric value based on the metric type
        
        Args:
            value: The value to format
            metric_name: The name of the metric (used for determining format)
            max_width: Maximum width for truncation
            
        Returns:
            Formatted value string
        """
        if value == '-' or value == 'N/A' or value is None:
            return '-'
        
        if isinstance(value, (int, float)):
            if metric_name in ['cpu', 'mem', 'disk']:
                formatted_value = f"{value}%"
            elif 'session' in metric_name:
                formatted_value = f"{value:,}"
            elif 'rate' in metric_name or 'lograte' in metric_name:
                formatted_value = f"{value}/s"
            elif 'tunnel' in metric_name:
                formatted_value = f"{value:,}"
            else:
                formatted_value = str(value)
        else:
            formatted_value = str(value)
        
        # Truncate if max_width specified
        if max_width and len(formatted_value) > max_width:
            formatted_value = formatted_value[:max_width-3] + "..."
        
        return formatted_value


class FortiGateAPIClient:
    """FortiGate API Client wrapper class"""
    
    def __init__(self, host: str, username: Optional[str] = None, password: Optional[str] = None, 
                 apikey: Optional[str] = None, use_ssl: bool = True, verify_ssl: bool = False,
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
    
    def execute_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None,
                       query_params: Optional[List[str]] = None) -> Tuple[int, Dict[str, Any]]:
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
                else:
                    # This should never happen due to validation above
                    return -5, {"error": "Unsupported method", "details": f"Method {method} not supported"}
                    
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

  # Get address objects (default table format)
  %(prog)s -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/address

  # Get address objects with specific table fields
  %(prog)s -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/address --table-fields name,subnet,type

  # Get firewall policies (default table format)
  %(prog)s -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/policy

  # Get raw JSON output (compact)
  %(prog)s -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/address --format json

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
    opt_group.add_argument('--format', choices=['json', 'pretty', 'table'], default='table',
                          help='Output format (default: table)')
    
    # Table-specific options
    table_group = parser.add_argument_group('Table Options')
    table_group.add_argument('--table-fields', metavar='FIELD1,FIELD2,...',
                            help='Comma-separated list of fields to include in table output')
    table_group.add_argument('--table-max-width', type=int, default=50, metavar='WIDTH',
                            help='Maximum width for table cell content (default: 50)')
    
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
        
        # Handle different output formats
        if args.format == 'table':
            # Parse table fields if provided
            custom_fields = None
            if args.table_fields:
                custom_fields = [field.strip() for field in args.table_fields.split(',')]
            
            # Format as table
            try:
                table_output = TableFormatter.format_table(
                    response, 
                    endpoint=args.endpoint,
                    custom_fields=custom_fields,
                    max_width=args.table_max_width
                )
                print(table_output)
            except Exception as e:
                print(f"Error formatting table: {e}", file=sys.stderr)
                print("Falling back to JSON output:")
                print(json.dumps(response, indent=2, default=str))
        elif args.format == 'json':
            # Raw JSON output
            print(f"Response: {json.dumps(response, default=str)}")
        else:  # pretty format (default)
            # Pretty JSON output
            print("Response:")
            print(json.dumps(response, indent=2, default=str))
        
        # Exit with non-zero code for errors
        # Handle both string and integer status codes
        if isinstance(status_code, int):
            if status_code < 0:
                sys.exit(1)
            elif status_code >= 400:
                sys.exit(2)
        elif isinstance(status_code, str):
            # String status codes like "success" are considered successful
            if status_code.lower() not in ['success', 'ok']:
                print(f"Warning: Unexpected status code: {status_code}", file=sys.stderr)
                sys.exit(1)
            
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)


if __name__ == '__main__':
    main()
