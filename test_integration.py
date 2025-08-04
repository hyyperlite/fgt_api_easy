#!/usr/bin/env python3
"""
Integration test for the table formatting functionality
"""

import json
import sys
import os

# Add the current directory to the path
sys.path.insert(0, '.')

from fgt_api_client import FortiGateAPIClient, TableFormatter

# Mock the FortiGate connection for testing
class MockFortiGate:
    def __init__(self, *args, **kwargs):
        self.closed = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.closed = True
    
    def get(self, endpoint, *args):
        # Return mock data based on endpoint
        if '/cmdb/firewall/address' in endpoint:
            return 200, {
                "results": [
                    {
                        "name": "test_host_1",
                        "subnet": "10.1.1.1/32",
                        "type": "ipmask",
                        "comment": "Test server 1"
                    },
                    {
                        "name": "test_host_2", 
                        "subnet": "10.1.1.2/32",
                        "type": "ipmask",
                        "comment": "Test server 2"
                    }
                ]
            }
        else:
            return 200, {"result": "success"}

def test_format_options():
    """Test different format options with mock data"""
    
    # Mock response data
    response_data = {
        "results": [
            {
                "name": "test_host_1",
                "subnet": "10.1.1.1/32", 
                "type": "ipmask",
                "comment": "Test server 1"
            },
            {
                "name": "test_host_2",
                "subnet": "10.1.1.2/32",
                "type": "ipmask", 
                "comment": "Test server 2"
            }
        ]
    }
    
    print("=== Testing Format Options ===\n")
    
    # Test JSON format
    print("1. JSON format:")
    json_output = json.dumps(response_data, default=str)
    print(f"Response: {json_output}")
    print("\n" + "="*50 + "\n")
    
    # Test pretty format
    print("2. Pretty format:")
    print("Response:")
    print(json.dumps(response_data, indent=2, default=str))
    print("\n" + "="*50 + "\n")
    
    # Test table format
    print("3. Table format:")
    table_output = TableFormatter.format_table(
        response_data,
        endpoint="/cmdb/firewall/address"
    )
    print(table_output)
    print("\n" + "="*50 + "\n")
    
    # Test table format with custom fields
    print("4. Table format with custom fields:")
    table_output = TableFormatter.format_table(
        response_data,
        endpoint="/cmdb/firewall/address",
        custom_fields=['name', 'subnet']
    )
    print(table_output)
    print("\n" + "="*50 + "\n")
    
    # Test table format with width limit
    print("5. Table format with width limit:")
    table_output = TableFormatter.format_table(
        response_data,
        endpoint="/cmdb/firewall/address",
        max_width=15
    )
    print(table_output)

if __name__ == "__main__":
    test_format_options()
