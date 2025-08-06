#!/usr/bin/env python3
"""
FortiGate API Client - AI/ML Integration Test Suite

Quick verification that all AI/ML components are working correctly.
This script runs through the essential functionality without requiring
a real FortiGate device.
"""

import sys
import os
import subprocess
import json
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def run_test(description, command, expect_success=True):
    """Run a test command and report results"""
    print(f"\n🔹 {description}")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"   ✅ SUCCESS")
            if result.stdout.strip():
                # Show first few lines of output
                lines = result.stdout.strip().split('\n')[:3]
                for line in lines:
                    if line.strip():
                        print(f"   📄 {line[:80]}...")
            return True
        else:
            print(f"   ❌ FAILED (exit code: {result.returncode})")
            if result.stderr.strip():
                print(f"   🚨 Error: {result.stderr.strip()[:100]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ⏰ TIMEOUT (>30s)")
        return False
    except Exception as e:
        print(f"   💥 ERROR: {e}")
        return False

def test_imports():
    """Test that all ML components can be imported"""
    print_header("Import Tests")
    
    import_tests = [
        ("Context Classifier", "python3 -c 'from ml_components.context_classifier import EndpointContextClassifier; print(\"✅ OK\")'"),
        ("Query Processor", "python3 -c 'from ml_components.query_processor import QueryProcessor; print(\"✅ OK\")'"),
        ("Display Engine", "python3 -c 'from ml_components.display_optimizer import IntelligentDisplayEngine; print(\"✅ OK\")'"),
        ("Model Trainer", "python3 -c 'from ml_components.model_trainer import MLModelTrainer; print(\"✅ OK\")'"),
    ]
    
    results = []
    for desc, cmd in import_tests:
        results.append(run_test(desc, cmd))
    
    return all(results)

def test_basic_functionality():
    """Test basic AI/ML functionality"""
    print_header("Basic Functionality Tests")
    
    functionality_tests = [
        ("AI Status Check", "python3 fgt_api_client.py --ai-status"),
        ("ML Demo", "python3 ml_demo.py"),
        ("Basic ML Test", "python3 test_ml_basic.py"),
    ]
    
    results = []
    for desc, cmd in functionality_tests:
        results.append(run_test(desc, cmd))
    
    return all(results)

def test_training_pipeline():
    """Test the training and data generation pipeline"""
    print_header("Training Pipeline Tests")
    
    training_tests = [
        ("Generate Training Data", "python3 generate_enhanced_training_data.py"),
        ("Train Enhanced Models", "python3 train_enhanced_models.py"),
    ]
    
    results = []
    for desc, cmd in training_tests:
        results.append(run_test(desc, cmd))
    
    return all(results)

def test_individual_components():
    """Test individual ML components"""
    print_header("Individual Component Tests")
    
    component_test = '''
import sys
sys.path.append('.')
from ml_components.context_classifier import EndpointContextClassifier
from ml_components.query_processor import QueryProcessor
from ml_components.display_optimizer import IntelligentDisplayEngine

# Test classifier
classifier = EndpointContextClassifier()
result = classifier.classify_endpoint_data('/cmdb/firewall/policy', {'policyid': 1, 'name': 'test'})
print(f"Classifier: {result['category']} ({result['confidence']:.2f})")

# Test query processor
processor = QueryProcessor()
result = processor.process_query('show enabled policies', {})
print(f"Query Processor: {result['intent']}")

# Test display engine
display = IntelligentDisplayEngine()
result = display.optimize_display('/cmdb/firewall/policy', {'policyid': 1})
print(f"Display Engine: {len(result['selected_fields'])} fields")

print("✅ All components working")
'''
    
    with open('/tmp/component_test.py', 'w') as f:
        f.write(component_test)
    
    return run_test("Component Integration", "python3 /tmp/component_test.py")

def check_training_data():
    """Check if training data exists and is valid"""
    print_header("Training Data Verification")
    
    training_dir = "ml_components/training_data"
    
    if not os.path.exists(training_dir):
        print("❌ Training data directory not found")
        return False
    
    # Count training files
    files = [f for f in os.listdir(training_dir) if f.endswith('.json')]
    print(f"📊 Found {len(files)} training data files")
    
    # Check for enhanced data
    enhanced_files = [f for f in files if f.startswith('enhanced_training_data_')]
    if enhanced_files:
        print(f"✅ Enhanced training data available: {len(enhanced_files)} files")
        
        # Load and check latest enhanced data
        latest_file = sorted(enhanced_files)[-1]
        filepath = os.path.join(training_dir, latest_file)
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            examples = len(data.get('examples', []))
            categories = len(data.get('categories', []))
            print(f"📈 Latest dataset: {examples} examples, {categories} categories")
            
            if examples >= 50 and categories >= 5:
                print("✅ Training data quality: GOOD")
                return True
            else:
                print("⚠️ Training data quality: NEEDS IMPROVEMENT")
                return False
                
        except Exception as e:
            print(f"❌ Error reading training data: {e}")
            return False
    else:
        print("⚠️ No enhanced training data found")
        return False

def check_model_files():
    """Check if trained model files exist"""
    print_header("Model Files Verification")
    
    models_dir = "ml_components/models"
    expected_files = ["classifier.pkl", "vectorizer.pkl", "categories.json"]
    
    if not os.path.exists(models_dir):
        print("❌ Models directory not found")
        return False
    
    existing_files = os.listdir(models_dir)
    missing_files = [f for f in expected_files if f not in existing_files]
    
    if missing_files:
        print(f"⚠️ Missing model files: {missing_files}")
        print("💡 Run 'python3 train_enhanced_models.py' to generate models")
        return False
    else:
        print("✅ All model files present")
        return True

def generate_summary_report(test_results):
    """Generate a summary report of all tests"""
    print_header("TEST SUMMARY REPORT")
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    print(f"\n📊 Overall Results: {passed}/{total} tests passed")
    print(f"🎯 Success Rate: {(passed/total)*100:.1f}%")
    
    print("\n📋 Individual Test Results:")
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:30} : {status}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! AI/ML integration is working correctly.")
        print("\n🚀 Ready for production use:")
        print("   • Run 'python3 ai_ml_usage_examples.py' for usage examples")
        print("   • See 'AI_ML_QUICK_REFERENCE.md' for command reference")
        print("   • Check 'ML_AI_IMPLEMENTATION_SUMMARY.md' for full documentation")
    else:
        print(f"\n⚠️ {total-passed} tests failed. Please review the errors above.")
        
        if not test_results.get("Training Data", False):
            print("\n💡 To fix training data issues:")
            print("   1. Run: python3 generate_enhanced_training_data.py")
            print("   2. Run: python3 train_enhanced_models.py")
        
        if not test_results.get("Model Files", False):
            print("\n💡 To generate model files:")
            print("   Run: python3 train_enhanced_models.py")

def main():
    """Run the complete test suite"""
    print("🤖 FortiGate API Client - AI/ML Integration Test Suite")
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Testing all AI/ML components without requiring FortiGate device")
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    test_results = {}
    
    # Run all test categories
    test_results["Import Tests"] = test_imports()
    test_results["Training Data"] = check_training_data() 
    test_results["Model Files"] = check_model_files()
    test_results["Component Tests"] = test_individual_components()
    test_results["Basic Functionality"] = test_basic_functionality()
    test_results["Training Pipeline"] = test_training_pipeline()
    
    # Generate final report
    generate_summary_report(test_results)
    
    # Clean up temp files
    try:
        os.remove('/tmp/component_test.py')
    except:
        pass
    
    # Exit with appropriate code
    all_passed = all(test_results.values())
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
