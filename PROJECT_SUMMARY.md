# FortiGate API Generic Client - Project Summary

## Overview
This project provides a comprehensive Python-based command-line interface for interacting with FortiGate devices using the pyfgt library. The application supports both API key and username/password authentication, configuration files, and all standard HTTP methods.

## Project Structure

```
fgt_api_generic/
├── fgt_api_client.py       # Main application script
├── fgt                     # Shell wrapper script for easier usage
├── test_client.py          # Test suite for functionality validation
├── examples.py             # Usage examples and demonstrations
├── requirements.txt        # Python package dependencies
├── Makefile               # Common operations automation
├── README.md              # Comprehensive documentation
├── config.ini.example     # Example INI configuration file
├── config.json.example    # Example JSON configuration file
└── __pycache__/           # Python bytecode cache
```

## Key Features

### Authentication Methods
- **API Key Authentication** (Recommended): More secure, no session management needed
- **Username/Password Authentication**: Traditional login method with session management

### Configuration Options
- **Command-line arguments**: Direct specification of all parameters
- **Configuration files**: Support for both INI and JSON formats
- **Flexible parameter precedence**: Command-line overrides config file values

### HTTP Methods Supported
- **GET**: Retrieve configuration and monitoring data
- **POST**: Create new objects
- **PUT**: Update existing objects  
- **DELETE**: Remove objects

### Advanced Features
- **Query Parameters**: Support for filtering, formatting, VDOM selection
- **JSON Data Input**: Structured data for POST/PUT operations
- **Multiple Output Formats**: JSON, pretty JSON, and table formats
- **Table Output**: Clean tabular display with auto-field detection for common objects
- **Customizable Tables**: Custom field selection and width control
- **Clean Output**: SSL warnings suppressed by default for better user experience
- **Comprehensive Error Handling**: Specific exceptions for different error types
- **Debug Mode**: Detailed logging for troubleshooting
- **SSL Configuration**: Options for SSL usage and certificate verification

## Usage Examples

### Basic Usage
```bash
# Get all firewall address objects
./fgt -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/address

# Create a new address object
./fgt -i 192.168.1.99 -k your_api_key -m post -e /cmdb/firewall/address \
  -d '{"name": "test_host", "subnet": "10.1.1.1/32"}'

# Use configuration file
./fgt -c config.ini -m get -e /cmdb/firewall/address
```

### Advanced Usage
```bash
# Get filtered results with specific formatting
./fgt -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/address \
  -q 'vdom=root' -q 'format=name' -q 'filter=name==test_object'

# Debug mode with SSL options
./fgt -i 192.168.1.99 -k your_api_key -m get -e /monitor/system/status \
  --debug --verify-ssl --timeout 60

# Disable pretty printing for compact output  
./fgt -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/address --format json

# Enable SSL warnings for security debugging
./fgt -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/address --ssl-warnings

# Table format for better readability
./fgt -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/address --format table

# Table format with specific fields
./fgt -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/policy --format table --table-fields policyid,name,action,status
```

## Installation and Setup

1. **Install Dependencies**:
   ```bash
   make install
   # OR
   pip install git+https://github.com/p4r4n0y1ng/pyfgt.git requests tabulate
   ```

2. **Run Tests**:
   ```bash
   make test
   # OR
   python3 test_client.py
   ```

3. **View Examples**:
   ```bash
   make examples
   # OR
   python3 examples.py
   ```

## Configuration Files

### INI Format
```ini
[fortigate]
host = 192.168.1.99
apikey = your_api_key_here
username = admin
debug = false
```

### JSON Format
```json
{
  "fortigate": {
    "host": "192.168.1.99",
    "apikey": "your_api_key_here",
    "username": "admin",
    "debug": false
  }
}
```

## Common FortiGate API Endpoints

### Configuration (CMDB)
- `/cmdb/firewall/address` - Address objects
- `/cmdb/firewall/addrgrp` - Address groups
- `/cmdb/firewall/policy` - Firewall policies
- `/cmdb/system/interface` - Network interfaces
- `/cmdb/router/static` - Static routes

### Monitoring
- `/monitor/system/status` - System status
- `/monitor/system/resource/usage` - Resource usage
- `/monitor/firewall/session` - Active sessions
- `/monitor/router/ipv4` - Routing table

## Error Handling

The application provides comprehensive error handling with specific exit codes:
- **0**: Success
- **1**: Configuration/validation errors
- **2**: HTTP errors (4xx/5xx)
- **130**: User cancellation (Ctrl+C)

## Security Considerations

1. **Use API Keys**: Preferred over username/password for better security
2. **Protect Configuration Files**: Use appropriate file permissions (600)
3. **SSL Verification**: Consider using `--verify-ssl` in production
4. **SSL Warnings**: Disabled by default for clean output; use `--ssl-warnings` for security debugging
5. **Credential Management**: Never hardcode credentials in scripts

## Testing and Validation

The project includes comprehensive testing:
- **Unit Tests**: Configuration parsing, data validation, client creation
- **Integration Examples**: Real-world usage patterns
- **Error Scenario Testing**: Invalid inputs and network failures

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure pyfgt is installed correctly
2. **Connection Timeouts**: Check network connectivity and firewall rules
3. **Authentication Failures**: Verify API key or credentials
4. **SSL Errors**: Use `--no-ssl` for HTTP or `--verify-ssl` for proper certificates

### Debug Mode
Use `--debug` flag for detailed troubleshooting information including:
- HTTP request/response details
- Connection information
- API call traces

## Future Enhancements

Potential improvements could include:
- Interactive mode for multiple operations
- Bulk operations from CSV/JSON files
- Output formatting options (CSV, XML)
- Configuration backup/restore utilities
- Integration with configuration management tools

## Dependencies

- **Python 3.6+**
- **pyfgt**: FortiGate API library
- **requests**: HTTP library (dependency of pyfgt)
- **configparser**: Configuration file parsing (built-in)
- **argparse**: Command-line argument parsing (built-in)
- **json**: JSON data handling (built-in)

This project provides a robust, flexible, and user-friendly interface for FortiGate API operations, suitable for both interactive use and automation scripts.
