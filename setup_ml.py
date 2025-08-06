#!/usr/bin/env python3
"""
ML/AI Setup Script for FortiGate API Client

This script helps set up the ML/AI components and verifies the installation.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"Error: Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def install_requirements():
    """Install required packages"""
    print("\nInstalling ML/AI requirements...")
    
    # Check if requirements.txt exists
    req_file = Path(__file__).parent / 'requirements.txt'
    if not req_file.exists():
        print("Error: requirements.txt not found")
        return False
    
    try:
        # Install requirements
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', str(req_file)
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            print("Error installing requirements:")
            print(result.stderr)
            return False
        
        print("✓ Requirements installed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        print("Error: Installation timed out")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def verify_ml_imports():
    """Verify that ML components can be imported"""
    print("\nVerifying ML component imports...")
    
    try:
        # Test basic ML dependencies
        import sklearn
        print(f"✓ scikit-learn {sklearn.__version__}")
        
        import pandas
        print(f"✓ pandas {pandas.__version__}")
        
        import numpy
        print(f"✓ numpy {numpy.__version__}")
        
        # Test sentence transformers (optional)
        try:
            import sentence_transformers
            print(f"✓ sentence-transformers {sentence_transformers.__version__}")
        except ImportError:
            print("⚠ sentence-transformers not available (optional)")
        
        # Test local ML components
        sys.path.insert(0, str(Path(__file__).parent))
        from ml_components import EndpointContextClassifier, IntelligentDisplayEngine, QueryProcessor, MLModelTrainer
        print("✓ FortiGate ML components imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"Error importing ML components: {e}")
        return False


def setup_directories():
    """Set up required directories"""
    print("\nSetting up directories...")
    
    base_dir = Path(__file__).parent
    directories = [
        base_dir / 'ml_components' / 'models',
        base_dir / 'ml_components' / 'training_data'
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created/verified directory: {directory}")
    
    return True


def create_sample_config():
    """Create sample configuration files"""
    print("\nCreating sample configuration...")
    
    base_dir = Path(__file__).parent
    
    # Create sample config.ini if it doesn't exist
    config_ini = base_dir / 'config.ini.example'
    if not config_ini.exists():
        sample_ini = """[fortigate]
host = 192.168.1.99
apikey = your_api_key_here
# or use username/password:
# username = admin  
# password = your_password

# ML/AI settings
enable_ml = true
collect_training_data = false
"""
        config_ini.write_text(sample_ini)
        print(f"✓ Created sample configuration: {config_ini}")
    
    return True


def run_basic_tests():
    """Run basic functionality tests"""
    print("\nRunning basic tests...")
    
    try:
        # Test ML components
        sys.path.insert(0, str(Path(__file__).parent))
        
        from ml_components import EndpointContextClassifier
        classifier = EndpointContextClassifier()
        
        # Test classification
        test_result = classifier.classify_endpoint_data(
            '/cmdb/firewall/policy',
            {'policyid': 1, 'name': 'test', 'action': 'accept'}
        )
        
        if test_result['category'] == 'firewall_policy':
            print("✓ Endpoint classification working")
        else:
            print(f"⚠ Unexpected classification result: {test_result['category']}")
        
        # Test display engine
        from ml_components import IntelligentDisplayEngine
        display_engine = IntelligentDisplayEngine(classifier)
        
        display_result = display_engine.optimize_display(
            '/cmdb/firewall/policy',
            [{'name': 'test_policy', 'status': 'enabled'}]
        )
        
        if display_result['context']:
            print("✓ Display optimization working")
        else:
            print("⚠ Display optimization issue")
        
        # Test query processor
        from ml_components import QueryProcessor
        processor = QueryProcessor(use_embeddings=False)  # Skip embeddings for quick test
        
        query_result = processor.process_query("show only enabled policies")
        
        if query_result['primary_intent'] == 'filter':
            print("✓ Query processing working")
        else:
            print(f"⚠ Unexpected query intent: {query_result['primary_intent']}")
        
        return True
        
    except Exception as e:
        print(f"Error during testing: {e}")
        return False


def check_training_data():
    """Check if training data exists"""
    print("\nChecking training data...")
    
    base_dir = Path(__file__).parent
    training_data_dir = base_dir / 'ml_components' / 'training_data'
    
    bootstrap_file = training_data_dir / 'bootstrap_training_data.json'
    if bootstrap_file.exists():
        try:
            with open(bootstrap_file, 'r') as f:
                data = json.load(f)
            print(f"✓ Bootstrap training data found: {data.get('total_examples', 0)} examples")
        except Exception as e:
            print(f"⚠ Bootstrap training data corrupted: {e}")
    else:
        print("⚠ No bootstrap training data found")
    
    return True


def main():
    """Main setup function"""
    print("FortiGate API Client - ML/AI Setup")
    print("=" * 40)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Install requirements
    if success and not install_requirements():
        success = False
    
    # Verify imports
    if success and not verify_ml_imports():
        success = False
    
    # Setup directories
    if success and not setup_directories():
        success = False
    
    # Create sample config
    if success and not create_sample_config():
        success = False
    
    # Check training data
    if success:
        check_training_data()
    
    # Run basic tests
    if success and not run_basic_tests():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("✓ ML/AI setup completed successfully!")
        print("\nNext steps:")
        print("1. Copy config.ini.example to config.ini and update with your FortiGate details")
        print("2. Run the demo: python3 ml_demo.py")
        print("3. Test with API client: ./fgt --ai-status -c config.ini")
        print("4. Train models: ./fgt --train-models -c config.ini")
        print("5. Use AI features: ./fgt --enable-ai --ai-query 'show only enabled' -c config.ini -m get -e /cmdb/firewall/policy")
    else:
        print("✗ Setup failed. Please check the errors above and try again.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
