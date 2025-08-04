# FortiGate API Generic Client

A simple Python command-line application for interacting with FortiGate devices using the [pyfgt](https://github.com/p4r4n0y1ng/pyfgt) library.

## Features

- Support for both API key and username/password authentication
- Configuration file support (INI and JSON formats)
- All HTTP methods (GET, POST, PUT, DELETE)
- Query parameter support for filtering and formatting
- JSON data input for POST/PUT requests
- Pretty-printed JSON output
- Comprehensive error handling
- Debug mode support

## Installation

1. Clone or download this repository
2. Install the required packages:
   ```bash
   pip install git+https://github.com/p4r4n0y1ng/pyfgt.git requests
   ```

## Usage

### Command Line Arguments

The application accepts various command-line arguments for configuration and API requests:

#### Connection Options
- `-c, --config`: Configuration file path (INI or JSON format)
- `-i, --host, --ip`: FortiGate IP address or hostname
- `-u, --username`: Username (default: admin)
- `-p, --password`: Password for authentication
- `-k, --apikey`: API key for authentication

#### Request Options
- `-m, --method`: HTTP method (get, post, put, delete) - **Required**
- `-e, --endpoint`: API endpoint path - **Required**
- `-d, --data`: Request data as JSON string (for POST/PUT)
- `-q, --query`: Query parameters (can be used multiple times)

#### Additional Options
- `--no-ssl`: Use HTTP instead of HTTPS
- `--verify-ssl`: Verify SSL certificates
- `--ssl-warnings`: Enable SSL warnings (disabled by default for cleaner output)
- `--timeout`: Request timeout in seconds (default: 300)
- `--debug`: Enable debug mode
- `--no-pretty`: Disable pretty print JSON output (pretty print is enabled by default)
- `--pretty`: Enable pretty print JSON output (default, kept for compatibility)

### Examples

#### Using API Key (Recommended)
```bash
# Get all firewall address objects
python3 fgt_api_client.py -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/address

# Get address objects with filtering and formatting
python3 fgt_api_client.py -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/address -q 'vdom=root' -q 'format=name' -q 'filter=name==test_object'

# Create a new address object
python3 fgt_api_client.py -i 192.168.1.99 -k your_api_key -m post -e /cmdb/firewall/address -d '{"name": "test_host", "subnet": "10.1.1.1/32", "type": "ipmask"}'

# Create an address group
python3 fgt_api_client.py -i 192.168.1.99 -k your_api_key -m post -e /cmdb/firewall/addrgrp -d '{"name": "test_group", "member": [{"name": "test_host"}]}'

# Update an existing address object
python3 fgt_api_client.py -i 192.168.1.99 -k your_api_key -m put -e /cmdb/firewall/address/test_host -d '{"subnet": "10.1.1.2/32"}'

# Delete an address object
python3 fgt_api_client.py -i 192.168.1.99 -k your_api_key -m delete -e /cmdb/firewall/address/test_host
```

#### Using Configuration File
```bash
# Create a configuration file (see examples below)
python3 fgt_api_client.py -c config.ini -m get -e /cmdb/firewall/address

# Disable pretty printing for compact output
python3 fgt_api_client.py -c config.ini -m get -e /cmdb/firewall/address --no-pretty
```

#### Using Username/Password
```bash
python3 fgt_api_client.py -i 192.168.1.99 -u admin -p password123 -m get -e /cmdb/firewall/address

# Enable SSL warnings for security debugging
python3 fgt_api_client.py -i 192.168.1.99 -u admin -p password123 -m get -e /cmdb/firewall/address --ssl-warnings
```

#### System Information Examples
```bash
# Get system status
python3 fgt_api_client.py -c config.ini -m get -e /monitor/system/status

# Get system interface information
python3 fgt_api_client.py -c config.ini -m get -e /cmdb/system/interface

# Get routing table
python3 fgt_api_client.py -c config.ini -m get -e /monitor/router/ipv4
```

## Configuration Files

The application supports both INI and JSON configuration file formats.

### INI Format (config.ini)
```ini
[fortigate]
host = 192.168.1.99
apikey = your_api_key_here
# Alternative: use username/password instead of API key
# username = admin
# password = your_password_here

# Optional settings
# use_ssl = true
# verify_ssl = false  
# timeout = 300
# debug = false
```

### JSON Format (config.json)
```json
{
  "fortigate": {
    "host": "192.168.1.99",
    "apikey": "your_api_key_here",
    "username": "admin",
    "use_ssl": true,
    "verify_ssl": false,
    "timeout": 300,
    "debug": false
  }
}
```

## Common FortiGate API Endpoints

Here are some commonly used FortiGate API endpoints:

### Configuration (CMDB)
- `/cmdb/firewall/address` - Firewall address objects
- `/cmdb/firewall/addrgrp` - Firewall address groups
- `/cmdb/firewall/service/custom` - Custom services
- `/cmdb/firewall/service/group` - Service groups
- `/cmdb/firewall/policy` - Firewall policies
- `/cmdb/system/interface` - System interfaces
- `/cmdb/router/static` - Static routes
- `/cmdb/user/local` - Local users
- `/cmdb/vpn.ssl.web/portal` - SSL VPN portals

### Monitoring
- `/monitor/system/status` - System status information
- `/monitor/system/resource/usage` - System resource usage
- `/monitor/firewall/session` - Active firewall sessions
- `/monitor/log/device` - Device logs
- `/monitor/router/ipv4` - IPv4 routing table
- `/monitor/system/interface` - Interface statistics

## Query Parameters

Common query parameters that can be used with the `-q` option:

- `vdom=root` - Specify VDOM (Virtual Domain)
- `format=name` - Return only names of objects
- `format=count` - Return count of objects
- `filter=name==object_name` - Filter by specific criteria
- `filter=name=@test` - Filter with wildcard (contains "test")
- `datasource=1` - Include datasource information
- `skip=10` - Skip first 10 results
- `count=50` - Limit results to 50 items

## Error Handling

The application provides comprehensive error handling with specific exit codes:

- **Exit Code 0**: Success
- **Exit Code 1**: Configuration or validation errors
- **Exit Code 2**: HTTP errors (4xx/5xx status codes)
- **Exit Code 130**: Operation cancelled by user (Ctrl+C)

## Debugging

Use the `--debug` flag to enable detailed debug output, which will show:
- HTTP request/response details
- Connection information
- API call traces

## Security Notes

1. **API Keys**: Use API keys instead of passwords when possible for better security
2. **SSL Verification**: In production, consider using `--verify-ssl` for certificate validation
3. **SSL Warnings**: By default, SSL warnings are suppressed for cleaner output. Use `--ssl-warnings` to enable them for security debugging
4. **Configuration Files**: Protect configuration files containing credentials (use appropriate file permissions)

## Requirements

- Python 3.6+
- pyfgt library
- requests library

## License

This project is provided as-is for educational and testing purposes. Please ensure you comply with your organization's security policies when using this tool.
