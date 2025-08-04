# FortiGate API Generic Client

A simple Python command-line application for interacting with FortiGate devices using the [pyfgt](https://github.com/p4r4n0y1ng/pyfgt) library.

## Features

- Support for both API key and username/password authentication
- Configuration file support (INI and JSON formats)
- All HTTP methods (GET, POST, PUT, DELETE)
- Query parameter support for filtering and formatting
- JSON data input for POST/PUT requests
- Multiple output formats: JSON, pretty JSON, and table
- Table output with automatic field detection for common FortiGate objects
- Customizable table fields and formatting
- Comprehensive error handling
- Debug mode support

## Installation

### Option 1: Using Virtual Environment (Recommended)

Using a virtual environment is the recommended approach as it isolates the project dependencies from your system Python installation.

1. Clone or download this repository
2. Create and activate a virtual environment:
   ```bash
   # Create virtual environment
   python3 -m venv fgt_api_env
   
   # Activate virtual environment
   # On Linux/macOS:
   source fgt_api_env/bin/activate
   
   # On Windows:
   # fgt_api_env\Scripts\activate
   ```
3. Install the required packages:
   ```bash
   pip install git+https://github.com/p4r4n0y1ng/pyfgt.git requests tabulate
   ```
   
   Or use the requirements file:
   ```bash
   pip install -r requirements.txt
   ```

4. When finished, you can deactivate the virtual environment:
   ```bash
   deactivate
   ```

### Option 2: Global Python Installation

If you prefer to install packages globally (not recommended for production environments):

1. Clone or download this repository
2. Install the required packages globally:
   ```bash
   pip install git+https://github.com/p4r4n0y1ng/pyfgt.git requests tabulate
   ```
   
   Or use the requirements file:
   ```bash
   pip install -r requirements.txt
   ```

**Note:** Global installation may cause conflicts with other Python projects on your system. Virtual environments are strongly recommended.

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
- `--format`: Output format - json, pretty, or table (default: table)

#### Table Output Options
- `--table-fields`: Comma-separated list of fields to include in table output
- `--table-max-width`: Maximum width for table cell content (default: 50)

### Examples

#### Using API Key (Recommended)
```bash
# Get all firewall address objects
python3 fgt_api_client.py -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/address

# Get address objects with filtering and formatting (table format is default)
python3 fgt_api_client.py -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/address -q 'vdom=root' -q 'format=name' -q 'filter=name==test_object'

# Create a new address object
python3 fgt_api_client.py -i 192.168.1.99 -k your_api_key -m post -e /cmdb/firewall/address -d '{"name": "test_host", "subnet": "10.1.1.1/32", "type": "ipmask"}'

# Create an address group
python3 fgt_api_client.py -i 192.168.1.99 -k your_api_key -m post -e /cmdb/firewall/addrgrp -d '{"name": "test_group", "member": [{"name": "test_host"}]}'

# Update an existing address object
python3 fgt_api_client.py -i 192.168.1.99 -k your_api_key -m put -e /cmdb/firewall/address/test_host -d '{"subnet": "10.1.1.2/32"}'

# Delete an address object
python3 fgt_api_client.py -i 192.168.1.99 -k your_api_key -m delete -e /cmdb/firewall/address/test_host

# Get address objects (default table format)
python3 fgt_api_client.py -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/address

# Get address objects in table format with specific fields
python3 fgt_api_client.py -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/address --table-fields name,subnet,type,comment

# Get firewall policies with specific fields
python3 fgt_api_client.py -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/policy --table-fields policyid,name,srcintf,dstintf,action,status
```

#### Table Output Examples

**Note: Table format is now the default output format for better readability of FortiGate API responses.**

The table output format provides a clean, readable view of FortiGate API responses. Here are some examples:

### Sample Address Objects Output
```
FortiGate API: /cmdb/firewall/address (4 result(s))
+----------------------+-------------+--------+-----------------------------+
| name                 | subnet      | type   | comment                     |
+======================+=============+========+=============================+
| FIREWALL_AUTH_PORTAL | 0.0.0.0/0   | ipmask | Authentication portal       |
+----------------------+-------------+--------+-----------------------------+
| all                  | 0.0.0.0/0   | ipmask |                             |
+----------------------+-------------+--------+-----------------------------+
| google-dns           | 8.8.8.8/32  | ipmask | Google DNS Server           |
+----------------------+-------------+--------+-----------------------------+
| test_host            | 10.1.1.1/32 | ipmask | Test server for development |
+----------------------+-------------+--------+-----------------------------+
```

### Sample Firewall Policy Output
```
FortiGate API: /cmdb/firewall/policy (2 result(s))
+------------+-----------------+---------------+-----------+-----------+-----------+
|   policyid | name            | srcintf       | dstintf   | srcaddr   | dstaddr   |
+============+=================+===============+===========+===========+===========+
|          1 | Allow-Internal  | internal, dmz | wan1      | all       | all       |
+------------+-----------------+---------------+-----------+-----------+-----------+
|          2 | Block-Bad-Sites | internal      | wan1      | all       | bad-sites |
+------------+-----------------+---------------+-----------+-----------+-----------+
```

### Table Features

- **Auto-detection**: Automatically selects the most relevant fields for common FortiGate objects
- **Custom fields**: Use `--table-fields` to specify exactly which fields to display
- **Width control**: Use `--table-max-width` to limit cell content width
- **Complex data handling**: Lists and nested objects are automatically flattened for display
- **Clean formatting**: Uses grid-style tables with proper alignment

#### Using Configuration File
```bash
# Create a configuration file (see examples below)
python3 fgt_api_client.py -c config.ini -m get -e /cmdb/firewall/address

# Get compact JSON output (override default table format)
python3 fgt_api_client.py -c config.ini -m get -e /cmdb/firewall/address --format json
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

## Migration from Previous Versions

If you're upgrading from a previous version that used `--pretty` and `--no-pretty` flags:

- Replace `--pretty` with `--format pretty` 
- Replace `--no-pretty` with `--format json` 
- Note: The default format is now table instead of pretty JSON

The old flags have been removed in favor of the cleaner `--format` option. Table format is now the default for better readability of FortiGate API responses.

## Requirements

- Python 3.6+
- pyfgt library
- requests library
- tabulate library

## License

This project is provided as-is for educational and testing purposes. Please ensure you comply with your organization's security policies when using this tool.
