#!/usr/bin/env python3
"""
FortiGate API Client - Examples

This script demonstrates common usage patterns for the FortiGate API client.
Replace the configuration values with your actual FortiGate details.
"""

import subprocess
import sys
import json


def run_command(cmd, description):
    """Run a command and display the results"""
    print(f"\n{description}")
    print("=" * len(description))
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✓ Success:")
            print(result.stdout)
        else:
            print("✗ Error:")
            print(result.stderr)
            print(result.stdout)
    except subprocess.TimeoutExpired:
        print("✗ Command timed out")
    except Exception as e:
        print(f"✗ Failed to run command: {e}")


def main():
    """Demonstrate common FortiGate API operations"""
    
    # Configuration - REPLACE THESE VALUES WITH YOUR ACTUAL FORTIGATE DETAILS
    HOST = "192.168.1.99"
    API_KEY = "your_api_key_here"
    
    print("FortiGate API Client - Usage Examples")
    print("=====================================")
    print(f"Target Host: {HOST}")
    print(f"API Key: {'*' * (len(API_KEY) - 4) + API_KEY[-4:] if len(API_KEY) > 4 else '****'}")
    print("\nNOTE: Update the HOST and API_KEY variables in this script with your actual values")
    print("SSL warnings are disabled by default for cleaner output. Use --ssl-warnings to enable them.")
    
    base_cmd = ["python3", "fgt_api_client.py", "-i", HOST, "-k", API_KEY]
    
    # Example 1: Get system status
    run_command(
        base_cmd + ["-m", "get", "-e", "/monitor/system/status"],
        "Example 1: Get System Status (Pretty Print Default)"
    )
    
    # Example 2: Get all firewall address objects
    run_command(
        base_cmd + ["-m", "get", "-e", "/cmdb/firewall/address"],
        "Example 2: Get All Firewall Address Objects (Pretty Print Default)"
    )
    
    # Example 3: Get address objects with filtering
    run_command(
        base_cmd + ["-m", "get", "-e", "/cmdb/firewall/address", 
                   "-q", "vdom=root", "-q", "format=name"],
        "Example 3: Get Address Objects (Names Only, Root VDOM)"
    )
    
    # Example 4: Get system interfaces with compact output
    run_command(
        base_cmd + ["-m", "get", "-e", "/cmdb/system/interface", "--format", "json"],
        "Example 4: Get System Interfaces (Compact Output)"
    )
    
    # Example 4.5: Get firewall addresses with specific table fields
    run_command(
        base_cmd + ["-m", "get", "-e", "/cmdb/firewall/address", "--table-fields", "name,subnet,type"],
        "Example 4.5: Get Firewall Addresses (Table Format with Custom Fields)"
    )
    
    # Example 4.6: Get firewall policies (table format is default)
    run_command(
        base_cmd + ["-m", "get", "-e", "/cmdb/firewall/policy"],
        "Example 4.6: Get Firewall Policies (Default Table Format)"
    )
    
    # Example 5: Create a test address object (commented out to prevent accidental creation)
    create_data = {
        "name": "api_test_host",
        "subnet": "10.99.99.99/32",
        "type": "ipmask",
        "comment": "Created via API test"
    }
    
    print(f"\nExample 5: Create Address Object (Commented Out)")
    print("=" * 50)
    print("Command would be:")
    print(" ".join(base_cmd + ["-m", "post", "-e", "/cmdb/firewall/address", 
                              "-d", json.dumps(create_data)]))
    print("Data:", json.dumps(create_data, indent=2))
    print("\nUncomment the lines below to actually create the object:")
    print("# run_command(")
    print("#     base_cmd + [\"-m\", \"post\", \"-e\", \"/cmdb/firewall/address\",")
    print("#                \"-d\", json.dumps(create_data)],")
    print("#     \"Example 5: Create Test Address Object\"")
    print("# )")
    
    # Example 6: Using configuration file
    print(f"\nExample 6: Using Configuration File")
    print("=" * 50)
    print("1. Create a config.ini file:")
    print("""[fortigate]
host = 192.168.1.99
apikey = your_api_key_here""")
    print("\n2. Run command:")
    print("python3 fgt_api_client.py -c config.ini -m get -e /cmdb/firewall/address")
    print("# Note: Pretty printing is now enabled by default")
    
    print(f"\n\nAll examples completed!")
    print("For more information, see README.md or run: python3 fgt_api_client.py --help")


if __name__ == '__main__':
    main()
