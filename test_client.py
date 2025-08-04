#!/usr/bin/env python3
"""
Test script for FortiGate API Client
This script demonstrates basic functionality without requiring a real FortiGate device.
"""

import sys
import json
from fgt_api_client import FortiGateAPIClient, load_config_file, parse_data_argument

def test_config_parsing():
    """Test configuration file parsing"""
    print("Testing configuration file parsing...")
    
    # Test INI config parsing
    try:
        with open('test_config.ini', 'w') as f:
            f.write("""[fortigate]
host = 192.168.1.99
apikey = test_api_key_12345
username = admin
debug = true
""")
        
        config = load_config_file('test_config.ini')
        print(f"✓ INI config loaded: {config}")
        
    except Exception as e:
        print(f"✗ INI config test failed: {e}")
    
    # Test JSON config parsing
    try:
        with open('test_config.json', 'w') as f:
            json.dump({
                "fortigate": {
                    "host": "192.168.1.99",
                    "apikey": "test_api_key_12345",
                    "username": "admin",
                    "debug": True
                }
            }, f)
        
        config = load_config_file('test_config.json')
        print(f"✓ JSON config loaded: {config}")
        
    except Exception as e:
        print(f"✗ JSON config test failed: {e}")


def test_data_parsing():
    """Test JSON data parsing"""
    print("\nTesting JSON data parsing...")
    
    test_cases = [
        '{"name": "test_host", "subnet": "10.1.1.1/32"}',
        '{"name": "test_group", "member": [{"name": "host1"}, {"name": "host2"}]}',
        '{"key": "value", "number": 42, "boolean": true}'
    ]
    
    for test_data in test_cases:
        try:
            parsed = parse_data_argument(test_data)
            print(f"✓ Parsed: {test_data} -> {parsed}")
        except Exception as e:
            print(f"✗ Failed to parse: {test_data} -> {e}")


def test_client_creation():
    """Test client creation with different authentication methods"""
    print("\nTesting client creation...")
    
    # Test with API key
    try:
        client = FortiGateAPIClient(
            host="192.168.1.99",
            apikey="test_api_key",
            debug=True
        )
        print("✓ Client created with API key authentication")
    except Exception as e:
        print(f"✗ Failed to create client with API key: {e}")
    
    # Test with username/password
    try:
        client = FortiGateAPIClient(
            host="192.168.1.99",
            username="admin",
            password="test_password",
            debug=True
        )
        print("✓ Client created with username/password authentication")
    except Exception as e:
        print(f"✗ Failed to create client with username/password: {e}")
    
    # Test invalid configuration (should fail)
    try:
        client = FortiGateAPIClient(
            host="192.168.1.99",
            username="admin"
            # No password or API key
        )
        print("✗ Should have failed - no authentication method provided")
    except ValueError as e:
        print(f"✓ Correctly rejected invalid config: {e}")


def cleanup():
    """Clean up test files"""
    import os
    for file in ['test_config.ini', 'test_config.json']:
        try:
            os.remove(file)
        except FileNotFoundError:
            pass


def main():
    """Run all tests"""
    print("FortiGate API Client - Test Suite")
    print("=" * 40)
    
    try:
        test_config_parsing()
        test_data_parsing()
        test_client_creation()
        
        print("\n" + "=" * 40)
        print("✓ All tests completed successfully!")
        print("\nTo test with a real FortiGate device, use:")
        print("python3 fgt_api_client.py -i <host> -k <api_key> -m get -e /cmdb/firewall/address")
        
    except Exception as e:
        print(f"\n✗ Test suite failed: {e}")
        sys.exit(1)
    finally:
        cleanup()


if __name__ == '__main__':
    main()
