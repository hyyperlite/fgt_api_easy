# FortiGate API Client with AI/ML

An intelligent Python command-line application for interacting with FortiGate devices with built-in AI/ML capabilities for natural language queries and smart data formatting.

## ⚡ **Super Quick Start**

```bash
git clone <repository-url>
cd fgt_api_generic
./install.sh               # One-click installation
cp config.ini.example config.ini    # Copy config template
# Edit config.ini with your FortiGate IP and API key
./fgt --ai-status -c config.ini      # Verify everything works
```

## ✨ Features

### Core Functionality
- **Multi-format authentication**: API key or username/password
- **Flexible configuration**: INI and JSON config file support  
- **Complete REST API support**: GET, POST, PUT, DELETE operations
- **Smart data formatting**: Automatic table formatting for FortiGate objects
- **Comprehensive error handling**: Graceful error reporting and debugging

### 🤖 AI/ML Capabilities
- **Natural language queries**: "show only enabled policies", "format as CSV"
- **Intelligent data formatting**: Context-aware output optimization
- **Smart field selection**: Automatic extraction of relevant fields
- **Multiple output formats**: Tables, JSON, CSV, HTML, summaries
- **Content filtering**: Natural language-based data filtering
- **Intent classification**: Understands user intent and formats accordingly

## 🚀 Quick Start (Recommended)

### One-Click Installation
```bash
git clone <repository-url>
cd fgt_api_generic
./install.sh
```

### Manual Installation
```bash
git clone <repository-url>
cd fgt_api_generic

# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Verify installation
python3 setup_ml.py
```

### Configuration
```bash
# Copy and edit config file
cp config.ini.example config.ini
# Edit config.ini with your FortiGate IP and API key
```

### Quick Test
```bash
# Test basic functionality
./fgt --ai-status -c config.ini

# Try natural language queries  
./fgt --enable-ai --ai-query "show only enabled policies" -c config.ini -m get -e /cmdb/firewall/policy

# Interactive mode
./fgt --interactive -c config.ini
```

## 📦 Alternative Installation Methods

### Manual Installation

#### Option 1: Using Virtual Environment
```bash
# Create virtual environment
python3 -m venv fgt_api_env
source fgt_api_env/bin/activate  # On Windows: fgt_api_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify setup
python3 setup_ml.py
```

#### Option 2: Global Installation
```bash
# Install globally (not recommended for production)
pip install -r requirements.txt
python3 setup_ml.py
```

## ⚙️ Configuration

### Quick Config Setup
```bash
# Use the example config as template
cp config.ini.example config.ini

# Edit with your details
[fortigate]
host = 192.168.1.99
apikey = your_api_key_here
enable_ml = true
```

### Alternative Config Formats
The application supports both INI and JSON configuration formats. See `config.json.example` for JSON format.

## 🤖 AI/ML Features

### Natural Language Queries
Use natural language to interact with FortiGate data:

```bash
# Smart filtering
./fgt --enable-ai --ai-query "show only enabled policies" -c config.ini -m get -e /cmdb/firewall/policy

# Format conversion  
./fgt --enable-ai --ai-query "format as CSV" -c config.ini -m get -e /cmdb/firewall/address

# Field selection
./fgt --enable-ai --ai-query "show me just the name and status fields" -c config.ini -m get -e /cmdb/system/interface

# Data summaries
./fgt --enable-ai --ai-query "give me a brief summary" -c config.ini -m get -e /cmdb/firewall/policy
```

### Interactive Mode with AI
```bash
# Start interactive session with AI assistance
./fgt --interactive -c config.ini

# Example interactive commands:
fgt> show firewall policies as CSV from gw1
fgt> list interfaces where status is up
fgt> summarize VPN tunnel status
fgt> display only enabled policies in table format
```

### AI Status and Training
```bash
# Check AI system status
./fgt --ai-status -c config.ini

# Train models with real data (optional)
./fgt --train-models -c config.ini

# Demo AI capabilities
python3 ml_demo.py
```

## 📖 Usage Examples

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
- `--table-max-fields`: Maximum number of fields to auto-detect for table display (default: 6, set to 0 for unlimited)

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

# Get LLDP neighbors with unlimited fields (show all available data)
python3 fgt_api_client.py -i 192.168.1.99 -k your_api_key -m get -e /monitor/network/lldp/neighbors --table-max-fields 0

# Get LLDP neighbors with limited fields (default is 6)
python3 fgt_api_client.py -i 192.168.1.99 -k your_api_key -m get -e /monitor/network/lldp/neighbors --table-max-fields 8
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
- **Field limiting**: By default, limits display to 6 most relevant fields for readability (use `--table-max-fields 0` for unlimited)
- **Custom fields**: Use `--table-fields` to specify exactly which fields to display
- **Width control**: Use `--table-max-width` to limit cell content width
- **Complex data handling**: Lists and nested objects are automatically flattened for display
- **Clean formatting**: Uses grid-style tables with proper alignment
- **Special formatters**: Some endpoints (like VPN IPsec and certificates) use multi-table layouts for comprehensive data display

### Field Display Control

By default, table output is limited to 6 fields to maintain readability on standard terminal widths. This is especially useful for endpoints with many fields (like LLDP neighbors which can have 10+ fields). You can control this behavior:

- **Default**: Shows 6 most relevant fields: `--table-max-fields 6` (or omit the option)
- **Unlimited**: Shows all available fields: `--table-max-fields 0`  
- **Custom limit**: Shows specific number of fields: `--table-max-fields 8`
- **Exact fields**: Override auto-detection entirely: `--table-fields field1,field2,field3`

**Example**: LLDP neighbors normally shows fields like `mac`, `chassis_id`, `port`, `port_name`, `port_id`, `system_name` (6 fields), but with `--table-max-fields 0` you'll also see `system_desc`, `ttl`, `port_desc`, and `addresses`.

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

## 🔧 Troubleshooting

### Installation Issues
```bash
# If setup_ml.py fails, try manual verification:
python3 -c "import sklearn, pandas, numpy; print('ML dependencies OK')"
python3 -c "from ml_components import EndpointContextClassifier; print('ML components OK')"

# Check Python version (3.8+ required)
python3 --version

# Update pip if needed
pip install --upgrade pip
```

### AI/ML Issues
```bash
# Check AI system status
./fgt --ai-status -c config.ini

# Regenerate models if needed
./fgt --train-models -c config.ini

# Test with basic query first
./fgt --enable-ai --ai-query "show data" -c config.ini -m get -e /cmdb/system/status
```

### Connection Issues
```bash
# Test basic connectivity
./fgt --debug -c config.ini -m get -e /cmdb/system/status

# Check SSL settings
./fgt --no-ssl -c config.ini -m get -e /cmdb/system/status
```

## 📚 Additional Resources

- **AI/ML Quick Reference**: See `AI_ML_QUICK_REFERENCE.md` for detailed AI feature documentation
- **Demo Script**: Run `python3 ml_demo.py` to see AI capabilities
- **Configuration Examples**: Check `config/` directory for host configuration examples

## 🔐 Security Notes

- **API Keys**: Preferred over username/password authentication
- **SSL Verification**: Use `--verify-ssl` in production environments  
- **Configuration Security**: Protect config files with appropriate permissions (`chmod 600 config.ini`)
- **Local Processing**: All AI/ML processing is done locally - no external API calls

## 📋 Requirements

- Python 3.6+
- pyfgt library
- requests library
- tabulate library

## License

This project is provided as-is for educational and testing purposes. Please ensure you comply with your organization's security policies when using this tool.
