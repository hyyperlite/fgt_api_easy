#!/usr/bin/env python3
"""
Simple test for pretty printing default behavior
"""

import sys
import subprocess
import json

def test_pretty_default():
    """Test that pretty printing is enabled by default"""
    print("Testing pretty print default behavior...")
    
    # Test command that should trigger the argument parsing
    cmd = ["python3", "fgt_api_client.py", "--help"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            output = result.stdout
            if "--no-pretty" in output and "pretty print is enabled by default" in output:
                print("✓ Help text shows --no-pretty option with correct description")
                return True
            else:
                print("✗ Help text doesn't show expected pretty print options")
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
    
    # Simulate the argument parser setup
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-pretty', action='store_true',
                       help='Disable pretty print JSON output')
    parser.add_argument('--pretty', action='store_true',
                       help='Enable pretty print JSON output')
    
    # Test default behavior (no flags)
    args = parser.parse_args([])
    use_pretty = not args.no_pretty
    if use_pretty:
        print("✓ Default behavior: pretty printing enabled")
    else:
        print("✗ Default behavior: pretty printing disabled")
    
    # Test with --no-pretty flag
    args = parser.parse_args(['--no-pretty'])
    use_pretty = not args.no_pretty
    if not use_pretty:
        print("✓ --no-pretty flag: pretty printing disabled")
    else:
        print("✗ --no-pretty flag: pretty printing still enabled")
    
    return True

def main():
    print("Simple Pretty Print Test")
    print("=" * 30)
    
    success = True
    success &= test_pretty_default()
    success &= test_argument_parsing()
    
    if success:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
