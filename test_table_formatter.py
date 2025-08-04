#!/usr/bin/env python3
"""
Test script to verify the table formatter handles different data structures correctly
"""

from fgt_api_client import TableFormatter

def test_nested_dict_formatting():
    """Test the nested dict formatting (like virtual-wan health-check)"""
    
    # Simulate the response structure for virtual-wan health-check
    response_data = {
        "results": {
            "anycast_v4": {
                "gw1_wan1": {"status": "up"},
                "gw1_wan2": {"status": "down"},
                "gw2_wan1": {"status": "up"}
            },
            "anycast_v6": {
                "gw1_wan1": {"status": "down"},
                "gw1_wan2": {"status": "up"}
            }
        }
    }
    
    result = TableFormatter.format_table(response_data, "/monitor/virtual-wan/health-check")
    print("=== Nested Dict Test ===")
    print(result)
    print()

def test_time_series_formatting():
    """Test the time-series formatting (like system resource usage)"""
    
    response_data = {
        "results": {
            "cpu": [
                {
                    "current": 5,
                    "historical": {
                        "1-min": {"min": 3, "max": 7, "average": 5},
                        "10-min": {"min": 2, "max": 8, "average": 4}
                    }
                }
            ],
            "mem": [
                {
                    "current": 25,
                    "historical": {
                        "1-min": {"min": 23, "max": 27, "average": 25},
                        "10-min": {"min": 22, "max": 28, "average": 24}
                    }
                }
            ]
        }
    }
    
    result = TableFormatter.format_table(response_data, "/monitor/system/resource/usage")
    print("=== Time Series Test ===")
    print(result)
    print()

def test_regular_list_formatting():
    """Test regular list formatting"""
    
    response_data = {
        "results": [
            {"name": "interface1", "status": "up", "ip": "192.168.1.1"},
            {"name": "interface2", "status": "down", "ip": "192.168.1.2"}
        ]
    }
    
    result = TableFormatter.format_table(response_data, "/monitor/system/interface")
    print("=== Regular List Test ===")
    print(result)
    print()

if __name__ == "__main__":
    test_nested_dict_formatting()
    test_time_series_formatting()
    test_regular_list_formatting()
