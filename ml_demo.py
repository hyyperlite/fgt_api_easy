#!/usr/bin/env python3
"""
ML/AI Component Demo Script

Demonstrates the machine learning and AI capabilities of the FortiGate API client.
This script shows how to use the intelligent data processing features.
"""

import os
import sys
import json
from pathlib import Path

# Add the project directory to the Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

try:
    from ml_components import EndpointContextClassifier, IntelligentDisplayEngine, QueryProcessor, MLModelTrainer
except ImportError:
    print("Error: ML components not found. Please install requirements first:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def demo_endpoint_classification():
    """Demonstrate endpoint context classification"""
    print("=== Endpoint Context Classification Demo ===")
    
    classifier = EndpointContextClassifier()
    
    # Test data samples
    test_cases = [
        {
            'endpoint': '/cmdb/firewall/policy',
            'data': {'policyid': 1, 'name': 'Allow_Web', 'srcaddr': 'internal', 'dstaddr': 'all', 'action': 'accept'},
            'description': 'Firewall policy'
        },
        {
            'endpoint': '/cmdb/firewall/address',
            'data': {'name': 'web_server', 'type': 'ipmask', 'subnet': '10.0.1.100/32'},
            'description': 'Address object'
        },
        {
            'endpoint': '/cmdb/router/static',
            'data': {'dst': '0.0.0.0/0', 'gateway': '192.168.1.1', 'device': 'port1', 'distance': 10},
            'description': 'Static route'
        },
        {
            'endpoint': '/monitor/system/status',
            'data': {'hostname': 'FortiGate-100D', 'version': 'v7.0.0', 'serial': 'FGT123456'},
            'description': 'System status'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['description']}")
        print(f"   Endpoint: {test_case['endpoint']}")
        
        result = classifier.classify_endpoint_data(test_case['endpoint'], test_case['data'])
        
        print(f"   Category: {result['category']} (confidence: {result['confidence']:.2f})")
        print(f"   Suggested fields: {', '.join(result['suggested_fields'])}")
    
    print(f"\nAvailable categories: {', '.join(classifier.list_categories())}")


def demo_intelligent_display():
    """Demonstrate intelligent display optimization"""
    print("\n=== Intelligent Display Optimization Demo ===")
    
    # Create classifier and display engine
    classifier = EndpointContextClassifier()
    display_engine = IntelligentDisplayEngine(classifier)
    
    # Sample firewall policy data
    policy_data = [
        {'policyid': 1, 'name': 'Allow_Web', 'srcaddr': 'internal', 'dstaddr': 'all', 'service': 'HTTP', 'action': 'accept', 'status': 'enable'},
        {'policyid': 2, 'name': 'Block_Social', 'srcaddr': 'users', 'dstaddr': 'social_media', 'service': 'HTTPS', 'action': 'deny', 'status': 'enable'},
        {'policyid': 3, 'name': 'Allow_VPN', 'srcaddr': 'vpn_users', 'dstaddr': 'servers', 'service': 'ALL', 'action': 'accept', 'status': 'disable'}
    ]
    
    print("\n1. Basic optimization:")
    result = display_engine.optimize_display('/cmdb/firewall/policy', policy_data)
    
    print(f"   Context: {result['context']} (confidence: {result['confidence']:.2f})")
    print(f"   Suggested format: {result['display_config']['display_format']}")
    print(f"   Priority fields: {', '.join(result['display_config']['priority_fields'])}")
    print(f"   Items: {result['original_count']} → {result['processed_count']}")
    
    print("\n2. With user query 'show only enabled policies':")
    result = display_engine.optimize_display('/cmdb/firewall/policy', policy_data, user_query="show only enabled policies")
    
    if result['processed_data']['applied_filters']:
        print(f"   Applied filters: {', '.join(result['processed_data']['applied_filters'])}")
    print(f"   Items after filtering: {len(result['processed_data']['data'])}")
    
    if result.get('suggestions'):
        print("   AI suggestions:")
        for suggestion in result['suggestions']:
            print(f"     • {suggestion}")


def demo_query_processing():
    """Demonstrate natural language query processing"""
    print("\n=== Natural Language Query Processing Demo ===")
    
    processor = QueryProcessor()
    
    # Test queries
    test_queries = [
        "show only enabled policies",
        "sort by name descending", 
        "group by interface",
        "display as json format",
        "limit to top 10 results",
        "find policies containing web"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        result = processor.process_query(query)
        
        print(f"   Intent: {result['primary_intent']} (confidence: {result['confidence']:.2f})")
        if result['parameters']:
            print(f"   Parameters: {json.dumps(result['parameters'], indent=6)}")
        if result['execution_plan']:
            print("   Execution plan:")
            for step in result['execution_plan']:
                print(f"     • {step['action']}: {step['params']}")


def demo_model_training():
    """Demonstrate ML model training"""
    print("\n=== ML Model Training Demo ===")
    
    trainer = MLModelTrainer()
    
    print("1. Generating synthetic training data...")
    synthetic_data = trainer.generate_synthetic_training_data({})
    print(f"   Generated {len(synthetic_data)} synthetic examples")
    
    print("\n2. Loading bootstrap training data...")
    try:
        bootstrap_data = trainer.load_training_data('bootstrap_training_data.json')
        print(f"   Loaded {bootstrap_data['total_examples']} examples")
        print(f"   Categories: {', '.join(bootstrap_data['categories'])}")
    except FileNotFoundError:
        print("   Bootstrap data not found, using synthetic data")
        bootstrap_data = trainer.create_training_data(synthetic_data)
    
    print("\n3. Training classifier...")
    try:
        results = trainer.train_context_classifier(bootstrap_data)
        print(f"   Training accuracy: {results.get('accuracy', 'N/A'):.3f}")
        print(f"   Training samples: {results.get('training_samples', 0)}")
        print(f"   Test samples: {results.get('test_samples', 0)}")
        
        if 'training_summary' in results:
            summary = results['training_summary']
            if summary.get('recommendations'):
                print("   Recommendations:")
                for rec in summary['recommendations']:
                    print(f"     • {rec}")
    except Exception as e:
        print(f"   Training failed: {e}")


def demo_full_pipeline():
    """Demonstrate the full ML pipeline"""
    print("\n=== Full ML Pipeline Demo ===")
    
    # Sample API response
    sample_response = {
        'results': [
            {'policyid': 1, 'name': 'Allow_Web', 'srcaddr': 'internal', 'dstaddr': 'all', 'action': 'accept', 'status': 'enable'},
            {'policyid': 2, 'name': 'Block_P2P', 'srcaddr': 'users', 'dstaddr': 'all', 'action': 'deny', 'status': 'enable'},
            {'policyid': 3, 'name': 'Allow_Email', 'srcaddr': 'internal', 'dstaddr': 'mail_servers', 'action': 'accept', 'status': 'enable'},
            {'policyid': 4, 'name': 'Test_Rule', 'srcaddr': 'test', 'dstaddr': 'test', 'action': 'accept', 'status': 'disable'}
        ]
    }
    
    print("1. Initial data:")
    print(f"   {len(sample_response['results'])} firewall policies")
    
    # Initialize components
    classifier = EndpointContextClassifier()
    display_engine = IntelligentDisplayEngine(classifier)
    query_processor = QueryProcessor()
    
    # Process user query
    user_query = "show only enabled policies sorted by name"
    print(f"\n2. Processing query: '{user_query}'")
    
    query_result = query_processor.process_query(user_query)
    print(f"   Intent: {query_result['primary_intent']}")
    print(f"   Execution plan: {len(query_result['execution_plan'])} steps")
    
    # Apply intelligent display
    print("\n3. Applying intelligent display optimization...")
    display_result = display_engine.optimize_display(
        '/cmdb/firewall/policy',
        sample_response['results'],
        user_query
    )
    
    print(f"   Context: {display_result['context']}")
    print(f"   Original items: {display_result['original_count']}")
    print(f"   Processed items: {display_result['processed_count']}")
    
    if display_result['processed_data']['applied_filters']:
        print("   Applied filters:")
        for filter_info in display_result['processed_data']['applied_filters']:
            print(f"     • {filter_info}")
    
    # Show final processed data
    final_data = display_result['processed_data']['data']
    print(f"\n4. Final results ({len(final_data)} items):")
    for item in final_data:
        print(f"   • {item['name']} (ID: {item['policyid']}, Status: {item['status']})")


def main():
    """Run all demos"""
    print("FortiGate API Client - ML/AI Components Demo")
    print("=" * 50)
    
    try:
        demo_endpoint_classification()
        demo_intelligent_display()
        demo_query_processing()
        demo_model_training()
        demo_full_pipeline()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("\nTo use ML/AI features with the API client:")
        print("  ./fgt --enable-ai --ai-query 'show only enabled' -i <host> -k <apikey> -m get -e /cmdb/firewall/policy")
        print("  ./fgt --train-models -i <host> -k <apikey>")
        print("  ./fgt --ai-status -i <host> -k <apikey>")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
