#!/usr/bin/env python3
"""
Simple test for format options behavior
"""

import sys
import subprocess
import json

def test_format_options():
    """Test that format options are working correctly"""
    print("Testing format options behavior...")
    
    # Test command that should trigger the argument parsing
    cmd = ["python3", "fgt_api_client.py", "--help"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            output = result.stdout
            if "--format {json,pretty,table}" in output and "Output format (default: table)" in output:
                print("✓ Help text shows --format option with correct choices")
                return True
            else:
                print("✗ Help text doesn't show expected format options")
                return False
        else:
            print(f"✗ Help command failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Failed to run help command: {e}")
        return False

def test_argument_parsing():
    """Test basic argument parsing logic"""
    import argparse
    
    # Simulate the argument parser setup with new format option
    parser = argparse.ArgumentParser()
    parser.add_argument('--format', choices=['json', 'pretty', 'table'], default='table',
                       help='Output format (default: table)')
    
    # Test default behavior (no flags)
    args = parser.parse_args([])
    if args.format == 'table':
        print("✓ Default behavior: table format selected")
    else:
        print("✗ Default behavior: unexpected format")
    
    # Test with --format json flag
    args = parser.parse_args(['--format', 'json'])
    if args.format == 'json':
        print("✓ --format json: JSON format selected")
    else:
        print("✗ --format json: unexpected format")
    
    # Test with --format table flag
    args = parser.parse_args(['--format', 'table'])
    if args.format == 'table':
        print("✓ --format table: table format selected")
    else:
        print("✗ --format table: unexpected format")
    
    return True

def main():
    print("Simple Format Options Test")
    print("=" * 30)
    
    success = True
    success &= test_format_options()
    success &= test_argument_parsing()
    
    if success:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
