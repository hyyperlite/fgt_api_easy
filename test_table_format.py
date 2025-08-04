#!/usr/bin/env python3
"""
Test script for the table formatting functionality
"""

import sys
sys.path.insert(0, '.')

from fgt_api_client import TableFormatter

# Sample FortiGate address data
sample_address_data = {
    "results": [
        {
            "name": "FIREWALL_AUTH_PORTAL",
            "subnet": "0.0.0.0/0",
            "type": "ipmask",
            "comment": "Authentication portal"
        },
        {
            "name": "all",
            "subnet": "0.0.0.0/0", 
            "type": "ipmask",
            "comment": ""
        },
        {
            "name": "google-dns",
            "subnet": "8.8.8.8/32",
            "type": "ipmask",
            "comment": "Google DNS Server"
        },
        {
            "name": "test_host",
            "subnet": "10.1.1.1/32",
            "type": "ipmask",
            "comment": "Test server for development"
        }
    ]
}

# Sample policy data
sample_policy_data = {
    "results": [
        {
            "policyid": 1,
            "name": "Allow-Internal",
            "srcintf": [{"name": "internal"}, {"name": "dmz"}],
            "dstintf": [{"name": "wan1"}],
            "srcaddr": [{"name": "all"}],
            "dstaddr": [{"name": "all"}],
            "action": "accept",
            "status": "enable"
        },
        {
            "policyid": 2,
            "name": "Block-Bad-Sites",
            "srcintf": [{"name": "internal"}],
            "dstintf": [{"name": "wan1"}],
            "srcaddr": [{"name": "all"}],
            "dstaddr": [{"name": "bad-sites"}],
            "action": "deny",
            "status": "enable"
        }
    ]
}

def test_table_formatting():
    print("=== Testing Table Formatting ===\n")
    
    # Test 1: Address objects with auto-detection
    print("1. Address objects (auto-detected fields):")
    table_output = TableFormatter.format_table(
        sample_address_data, 
        endpoint="/cmdb/firewall/address"
    )
    print(table_output)
    print("\n" + "="*50 + "\n")
    
    # Test 2: Address objects with custom fields
    print("2. Address objects (custom fields):")
    table_output = TableFormatter.format_table(
        sample_address_data,
        endpoint="/cmdb/firewall/address",
        custom_fields=['name', 'subnet', 'comment']
    )
    print(table_output)
    print("\n" + "="*50 + "\n")
    
    # Test 3: Policy objects with auto-detection
    print("3. Firewall policies (auto-detected fields):")
    table_output = TableFormatter.format_table(
        sample_policy_data,
        endpoint="/cmdb/firewall/policy"
    )
    print(table_output)
    print("\n" + "="*50 + "\n")
    
    # Test 4: Policy objects with width limit
    print("4. Firewall policies (with width limit):")
    table_output = TableFormatter.format_table(
        sample_policy_data,
        endpoint="/cmdb/firewall/policy",
        max_width=20
    )
    print(table_output)

if __name__ == "__main__":
    test_table_formatting()
