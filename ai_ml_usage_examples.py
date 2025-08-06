#!/usr/bin/env python3
"""
FortiGate API Client - AI/ML Integration Usage Examples

This script demonstrates how to use the new AI/ML features with practical examples
for real-world FortiGate API interactions.
"""

import json
import subprocess
import sys
import os
from datetime import datetime

def run_command(cmd, description):
    """Run a command and display results"""
    print(f"\n{'=' * 60}")
    print(f"🧪 {description}")
    print(f"Command: {cmd}")
    print("=" * 60)
    
    try:
        # For demo purposes, we'll show the command structure
        # In real usage, replace with actual FortiGate credentials
        print("📝 Note: Replace <host> and <apikey> with your FortiGate details")
        print(f"💻 Example: {cmd}")
        
        # If this is a local test command (no host/apikey needed), run it
        if not any(x in cmd for x in ['-i ', '-k ', '<host>', '<apikey>']):
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Output:")
                print(result.stdout)
            else:
                print("❌ Error:")
                print(result.stderr)
        
    except Exception as e:
        print(f"❌ Error running command: {e}")

def main():
    """Demonstrate AI/ML usage examples"""
    
    print("🤖 FortiGate API Client - AI/ML Integration Usage Examples")
    print("=" * 70)
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("📋 PREREQUISITES:")
    print("   • FortiGate device with API access enabled")
    print("   • Valid API key with appropriate permissions")
    print("   • Network connectivity to FortiGate")
    print("   • ML models trained (run train_enhanced_models.py)")
    
    # 1. Basic AI Status Check
    run_command(
        "python3 fgt_api_client.py --ai-status",
        "Check AI/ML System Status"
    )
    
    # 2. AI-Enhanced API Queries
    print(f"\n{'🎯 AI-ENHANCED API QUERIES':=^70}")
    
    run_command(
        "python3 fgt_api_client.py --enable-ai -i <host> -k <apikey> -m get -e /cmdb/firewall/policy",
        "Basic AI-Enhanced Firewall Policy Retrieval"
    )
    
    run_command(
        "python3 fgt_api_client.py --enable-ai --ai-query 'show only enabled policies' -i <host> -k <apikey> -m get -e /cmdb/firewall/policy",
        "Natural Language Query: Show Only Enabled Policies"
    )
    
    run_command(
        "python3 fgt_api_client.py --enable-ai --ai-query 'sort by name descending' -i <host> -k <apikey> -m get -e /cmdb/firewall/address",
        "Natural Language Query: Sort Address Objects by Name"
    )
    
    run_command(
        "python3 fgt_api_client.py --enable-ai --ai-format summary -i <host> -k <apikey> -m get -e /cmdb/firewall/policy",
        "AI-Optimized Summary Format"
    )
    
    run_command(
        "python3 fgt_api_client.py --enable-ai --ai-query 'group by interface' -i <host> -k <apikey> -m get -e /cmdb/system/interface",
        "Natural Language Query: Group Interfaces by Type"
    )
    
    # 3. Different FortiGate Object Types
    print(f"\n{'🏗️ DIFFERENT FORTIGATE OBJECT TYPES':=^70}")
    
    run_command(
        "python3 fgt_api_client.py --enable-ai --ai-query 'show active VPN tunnels' -i <host> -k <apikey> -m get -e /monitor/vpn/ipsec",
        "VPN Monitoring with AI Processing"
    )
    
    run_command(
        "python3 fgt_api_client.py --enable-ai --ai-format table -i <host> -k <apikey> -m get -e /cmdb/router/static",
        "Routing Table with Intelligent Display"
    )
    
    run_command(
        "python3 fgt_api_client.py --enable-ai --ai-query 'find users with LDAP authentication' -i <host> -k <apikey> -m get -e /cmdb/user/ldap",
        "User Authentication Analysis"
    )
    
    run_command(
        "python3 fgt_api_client.py --enable-ai --ai-query 'show security profiles in use' -i <host> -k <apikey> -m get -e /cmdb/antivirus/profile",
        "Security Profile Analysis"
    )
    
    # 4. Training Data Collection
    print(f"\n{'📊 TRAINING DATA COLLECTION':=^70}")
    
    run_command(
        "python3 fgt_api_client.py --collect-training-data -i <host> -k <apikey> -m get -e /cmdb/firewall/policy",
        "Collect Training Data from Firewall Policies"
    )
    
    run_command(
        "python3 fgt_api_client.py --collect-training-data -i <host> -k <apikey> -m get -e /cmdb/firewall/address",
        "Collect Training Data from Address Objects"
    )
    
    # 5. Model Training
    print(f"\n{'🤖 MODEL TRAINING & MAINTENANCE':=^70}")
    
    run_command(
        "python3 fgt_api_client.py --train-models",
        "Train ML Models with Collected Data"
    )
    
    run_command(
        "python3 generate_enhanced_training_data.py",
        "Generate Enhanced Synthetic Training Data"
    )
    
    run_command(
        "python3 train_enhanced_models.py",
        "Train Models with Enhanced Dataset"
    )
    
    # 6. Local Testing (No FortiGate Required)
    print(f"\n{'🧪 LOCAL TESTING (NO FORTIGATE REQUIRED)':=^70}")
    
    run_command(
        "python3 ml_demo.py",
        "Comprehensive ML/AI Demo"
    )
    
    run_command(
        "python3 test_ml_basic.py",
        "Basic ML Component Testing"
    )
    
    # 7. Advanced Usage Examples
    print(f"\n{'⚡ ADVANCED USAGE PATTERNS':=^70}")
    
    print("\n🔄 Batch Processing Example:")
    batch_example = '''
# Process multiple endpoints with AI enhancement
for endpoint in /cmdb/firewall/policy /cmdb/firewall/address /cmdb/router/static; do
    python3 fgt_api_client.py --enable-ai --ai-format summary \\
        -i <host> -k <apikey> -m get -e "$endpoint"
done
    '''
    print(batch_example)
    
    print("\n📋 Configuration Audit Example:")
    audit_example = '''
# Audit firewall policies
python3 fgt_api_client.py --enable-ai --ai-query "show disabled policies" \\
    -i <host> -k <apikey> -m get -e /cmdb/firewall/policy

# Check for unused address objects
python3 fgt_api_client.py --enable-ai --ai-query "find unused objects" \\
    -i <host> -k <apikey> -m get -e /cmdb/firewall/address

# Review VPN status
python3 fgt_api_client.py --enable-ai --ai-query "show down VPN connections" \\
    -i <host> -k <apikey> -m get -e /monitor/vpn/ipsec
    '''
    print(audit_example)
    
    print("\n📈 Monitoring Dashboard Example:")
    dashboard_example = '''
# System performance overview
python3 fgt_api_client.py --enable-ai --ai-format summary \\
    -i <host> -k <apikey> -m get -e /monitor/system/performance

# Interface statistics
python3 fgt_api_client.py --enable-ai --ai-query "show top interfaces by traffic" \\
    -i <host> -k <apikey> -m get -e /monitor/system/interface

# Session analysis
python3 fgt_api_client.py --enable-ai --ai-query "group sessions by destination port" \\
    -i <host> -k <apikey> -m get -e /monitor/firewall/session
    '''
    print(dashboard_example)
    
    # 8. Troubleshooting Guide
    print(f"\n{'🔧 TROUBLESHOOTING GUIDE':=^70}")
    
    troubleshooting = [
        ("Check AI/ML status", "python3 fgt_api_client.py --ai-status"),
        ("Verify ML components", "python3 -c 'from ml_components import *; print(\"✅ All imports OK\")'"),
        ("Test classification", "python3 test_ml_basic.py"),
        ("Re-train models", "python3 train_enhanced_models.py"),
        ("Generate fresh data", "python3 generate_enhanced_training_data.py"),
        ("Run full demo", "python3 ml_demo.py")
    ]
    
    for desc, cmd in troubleshooting:
        print(f"\n❓ {desc}:")
        print(f"   {cmd}")
    
    # 9. Performance Tips
    print(f"\n{'⚡ PERFORMANCE TIPS':=^70}")
    
    tips = [
        "🎯 Use specific AI queries for better performance",
        "📊 Collect training data regularly for improved accuracy", 
        "🔄 Re-train models after collecting new data",
        "🎨 Use appropriate AI formats (table, summary, json) for your use case",
        "💾 Enable training data collection during normal API usage",
        "🧠 Review AI suggestions to understand optimal usage patterns"
    ]
    
    for tip in tips:
        print(f"   {tip}")
    
    print(f"\n{'=' * 70}")
    print("✅ Usage examples complete!")
    print()
    print("📚 For more information:")
    print("   • See ML_AI_IMPLEMENTATION_SUMMARY.md for full documentation")
    print("   • Run python3 ml_demo.py for interactive demonstration")
    print("   • Check ml_components/ directory for component details")
    print("=" * 70)

if __name__ == "__main__":
    main()
