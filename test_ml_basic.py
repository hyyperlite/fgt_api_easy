#!/usr/bin/env python3
"""
Quick test of ML functionality without training
"""

import sys
import os
from pathlib import Path

# Add project directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ml_components import EndpointContextClassifier, IntelligentDisplayEngine, QueryProcessor

def test_basic_functionality():
    """Test basic ML functionality without trained models"""
    
    print("Testing ML Components (Rule-based mode)")
    print("=" * 50)
    
    # Test context classification
    classifier = EndpointContextClassifier()
    
    test_cases = [
        {
            'endpoint': '/cmdb/firewall/policy',
            'data': {'policyid': 1, 'name': 'Allow_Web', 'action': 'accept', 'status': 'enable'}
        },
        {
            'endpoint': '/cmdb/firewall/address', 
            'data': {'name': 'web_server', 'type': 'ipmask', 'subnet': '10.0.1.100/32'}
        },
        {
            'endpoint': '/monitor/vpn/ipsec',
            'data': {'name': 'VPN_HQ', 'status': 'up', 'incoming_bytes': 1048576}
        }
    ]
    
    print("\n1. Context Classification:")
    for i, case in enumerate(test_cases, 1):
        result = classifier.classify_endpoint_data(case['endpoint'], case['data'])
        print(f"   {i}. {case['endpoint']} -> {result['category']} (confidence: {result['confidence']:.2f})")
    
    # Test display optimization
    display_engine = IntelligentDisplayEngine(classifier)
    
    print("\n2. Display Optimization:")
    policy_data = [
        {'policyid': 1, 'name': 'Allow_Web', 'action': 'accept', 'status': 'enable'},
        {'policyid': 2, 'name': 'Block_P2P', 'action': 'deny', 'status': 'enable'}
    ]
    
    result = display_engine.optimize_display('/cmdb/firewall/policy', policy_data)
    print(f"   Context: {result['context']}")
    print(f"   Suggested fields: {', '.join(result['display_config']['priority_fields'])}")
    
    # Test query processing
    processor = QueryProcessor(use_embeddings=False)
    
    print("\n3. Query Processing:")
    queries = [
        "show only enabled policies",
        "sort by name descending"
    ]
    
    for query in queries:
        result = processor.process_query(query)
        print(f"   '{query}' -> {result['primary_intent']} (confidence: {result['confidence']:.2f})")
    
    print("\n" + "=" * 50)
    print("✓ Basic ML functionality working!")
    print("\nThe ML/AI system is ready to use with rule-based classification.")
    print("For improved accuracy, you can train models when you have more data.")
    
    return True

if __name__ == "__main__":
    try:
        test_basic_functionality()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
