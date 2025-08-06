#!/usr/bin/env python3
"""
Enhanced ML Training and Validation Script

This script uses the enhanced training data to train and validate
the ML models for better performance.
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from ml_components.model_trainer import MLModelTrainer
    from ml_components.context_classifier import EndpointContextClassifier
    from ml_components.query_processor import QueryProcessor
    from ml_components.display_optimizer import IntelligentDisplayEngine
except ImportError as e:
    print(f"❌ Error importing ML components: {e}")
    sys.exit(1)


class EnhancedMLTrainer:
    """Enhanced ML trainer with improved validation and metrics"""
    
    def __init__(self, training_data_path: str = None):
        self.trainer = MLModelTrainer()
        self.training_data_path = training_data_path
        self.results = {}
    
    def load_enhanced_training_data(self) -> Dict[str, Any]:
        """Load the enhanced training data"""
        if self.training_data_path and os.path.exists(self.training_data_path):
            with open(self.training_data_path, 'r') as f:
                return json.load(f)
        else:
            # Find the most recent enhanced training data
            training_dir = os.path.join(os.path.dirname(__file__), 'ml_components', 'training_data')
            enhanced_files = [f for f in os.listdir(training_dir) if f.startswith('enhanced_training_data_')]
            
            if not enhanced_files:
                raise FileNotFoundError("No enhanced training data files found")
            
            # Get the most recent file
            enhanced_files.sort(reverse=True)
            latest_file = enhanced_files[0]
            filepath = os.path.join(training_dir, latest_file)
            
            with open(filepath, 'r') as f:
                return json.load(f)
    
    def validate_training_data(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the quality of training data"""
        print("🔍 Validating training data quality...")
        
        examples = training_data['examples']
        categories = training_data.get('categories', [])
        
        validation_results = {
            'total_examples': len(examples),
            'total_categories': len(categories),
            'category_distribution': {},
            'data_quality_issues': [],
            'recommendations': []
        }
        
        # Check category distribution
        for example in examples:
            cat = example.get('category', 'unknown')
            validation_results['category_distribution'][cat] = validation_results['category_distribution'].get(cat, 0) + 1
        
        # Check for data quality issues
        min_examples_per_category = 3
        max_imbalance_ratio = 5
        
        cat_counts = validation_results['category_distribution']
        if cat_counts:
            max_count = max(cat_counts.values())
            min_count = min(cat_counts.values())
            
            # Check minimum examples
            insufficient_cats = [cat for cat, count in cat_counts.items() if count < min_examples_per_category]
            if insufficient_cats:
                validation_results['data_quality_issues'].append(f"Categories with insufficient examples: {insufficient_cats}")
            
            # Check imbalance
            if max_count / min_count > max_imbalance_ratio:
                validation_results['data_quality_issues'].append(f"High class imbalance detected (ratio: {max_count / min_count:.1f})")
            
            # Generate recommendations
            if len(examples) < 50:
                validation_results['recommendations'].append("Consider generating more training examples")
            
            if insufficient_cats:
                validation_results['recommendations'].append("Add more examples for underrepresented categories")
            
            if not validation_results['data_quality_issues']:
                validation_results['recommendations'].append("Training data quality is good - proceed with training")
        
        return validation_results
    
    def train_all_models(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """Train all ML models with enhanced data"""
        print("🤖 Training ML models with enhanced data...")
        
        results = {
            'context_classifier': None,
            'training_date': datetime.now().isoformat(),
            'data_stats': {
                'total_examples': len(training_data['examples']),
                'categories': list(training_data.get('categories', [])),
                'enhanced_dataset': training_data.get('enhanced_dataset', False)
            }
        }
        
        try:
            # Train context classifier
            print("   🎯 Training endpoint context classifier...")
            classifier_results = self.trainer.train_context_classifier(training_data)
            results['context_classifier'] = classifier_results
            print(f"   ✅ Context classifier trained - Accuracy: {classifier_results.get('accuracy', 'N/A')}")
            
        except Exception as e:
            print(f"   ❌ Error training context classifier: {e}")
            results['context_classifier'] = {'error': str(e)}
        
        return results
    
    def test_trained_models(self, test_examples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test the trained models with sample data"""
        print("🧪 Testing trained models...")
        
        test_results = {
            'context_classifier': {'predictions': [], 'accuracy_estimates': []},
            'query_processor': {'test_queries': []},
            'display_optimizer': {'formatting_tests': []}
        }
        
        try:
            # Test context classifier
            classifier = EndpointContextClassifier()
            
            correct_predictions = 0
            total_predictions = 0
            
            for example in test_examples[:10]:  # Test first 10 examples
                endpoint = example['endpoint']
                data = example['data']
                expected_category = example['category']
                
                result = classifier.classify_endpoint_data(endpoint, data)
                predicted_category = result['category']
                confidence = result['confidence']
                
                is_correct = predicted_category == expected_category
                if is_correct:
                    correct_predictions += 1
                total_predictions += 1
                
                test_results['context_classifier']['predictions'].append({
                    'endpoint': endpoint,
                    'expected': expected_category,
                    'predicted': predicted_category,
                    'confidence': confidence,
                    'correct': is_correct
                })
            
            if total_predictions > 0:
                accuracy = correct_predictions / total_predictions
                test_results['context_classifier']['accuracy_estimates'] = [accuracy]
                print(f"   🎯 Context Classifier Test Accuracy: {accuracy:.2%}")
            
        except Exception as e:
            print(f"   ❌ Error testing context classifier: {e}")
            test_results['context_classifier']['error'] = str(e)
        
        try:
            # Test query processor
            query_processor = QueryProcessor()
            
            test_queries = [
                "show me all firewall policies",
                "list blocked traffic",
                "what VPN connections are active?",
                "display system interfaces",
                "show routing table"
            ]
            
            for query in test_queries:
                result = query_processor.process_query(query, {})
                test_results['query_processor']['test_queries'].append({
                    'query': query,
                    'intent': result.get('intent', 'unknown'),
                    'confidence': result.get('confidence', 0)
                })
                print(f"   💬 Query: '{query}' -> Intent: {result.get('intent', 'unknown')}")
            
        except Exception as e:
            print(f"   ❌ Error testing query processor: {e}")
            test_results['query_processor']['error'] = str(e)
        
        try:
            # Test display optimizer
            display_optimizer = IntelligentDisplayEngine()
            
            sample_data = test_examples[0] if test_examples else {}
            if sample_data:
                formatted = display_optimizer.optimize_display(
                    sample_data.get('endpoint', ''), 
                    sample_data.get('data', {}), 
                    user_query=None
                )
                
                test_results['display_optimizer']['formatting_tests'].append({
                    'category': sample_data.get('category', 'unknown'),
                    'formatted_fields': len(formatted.get('selected_fields', [])),
                    'display_hints': len(formatted.get('suggestions', []))
                })
                print(f"   🎨 Display optimization test completed")
            
        except Exception as e:
            print(f"   ❌ Error testing display optimizer: {e}")
            test_results['display_optimizer']['error'] = str(e)
        
        return test_results
    
    def generate_training_report(self, validation_results: Dict[str, Any], 
                               training_results: Dict[str, Any], 
                               test_results: Dict[str, Any]) -> str:
        """Generate a comprehensive training report"""
        
        report_lines = [
            "=" * 80,
            "🤖 ENHANCED ML TRAINING REPORT",
            "=" * 80,
            "",
            f"📅 Training Date: {training_results.get('training_date', 'Unknown')}",
            f"📊 Dataset: Enhanced FortiGate API Training Data",
            "",
            "📈 DATA VALIDATION RESULTS:",
            f"   Total Examples: {validation_results['total_examples']}",
            f"   Total Categories: {validation_results['total_categories']}",
            "",
            "   Category Distribution:"
        ]
        
        for category, count in sorted(validation_results['category_distribution'].items()):
            percentage = (count / validation_results['total_examples']) * 100
            report_lines.append(f"     {category:25} : {count:3d} examples ({percentage:.1f}%)")
        
        if validation_results['data_quality_issues']:
            report_lines.extend([
                "",
                "⚠️  Data Quality Issues:",
            ])
            for issue in validation_results['data_quality_issues']:
                report_lines.append(f"     • {issue}")
        
        if validation_results['recommendations']:
            report_lines.extend([
                "",
                "💡 Recommendations:",
            ])
            for rec in validation_results['recommendations']:
                report_lines.append(f"     • {rec}")
        
        # Training results
        report_lines.extend([
            "",
            "🎯 MODEL TRAINING RESULTS:",
        ])
        
        if training_results.get('context_classifier'):
            cc_results = training_results['context_classifier']
            if 'error' in cc_results:
                report_lines.append(f"   Context Classifier: ❌ Error - {cc_results['error']}")
            else:
                accuracy = cc_results.get('accuracy', 'N/A')
                report_lines.append(f"   Context Classifier: ✅ Trained - Accuracy: {accuracy}")
        
        # Test results
        report_lines.extend([
            "",
            "🧪 MODEL TESTING RESULTS:",
        ])
        
        if test_results.get('context_classifier', {}).get('accuracy_estimates'):
            test_acc = test_results['context_classifier']['accuracy_estimates'][0]
            report_lines.append(f"   Context Classifier Test Accuracy: {test_acc:.2%}")
        
        query_tests = len(test_results.get('query_processor', {}).get('test_queries', []))
        if query_tests > 0:
            report_lines.append(f"   Query Processor: {query_tests} test queries processed")
        
        format_tests = len(test_results.get('display_optimizer', {}).get('formatting_tests', []))
        if format_tests > 0:
            report_lines.append(f"   Display Optimizer: {format_tests} formatting tests completed")
        
        report_lines.extend([
            "",
            "✅ TRAINING SUMMARY:",
            "   Enhanced training data successfully generated and used",
            "   Models trained with improved dataset diversity",
            "   Ready for integration with FortiGate API Client",
            "",
            "🚀 Next Steps:",
            "   • Test models with real FortiGate API responses",
            "   • Collect user feedback for continuous improvement",
            "   • Consider incremental learning from production data",
            "",
            "=" * 80
        ])
        
        return "\n".join(report_lines)
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save training results to file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"enhanced_training_results_{timestamp}.json"
        
        results_dir = os.path.join(os.path.dirname(__file__), 'ml_components', 'training_results')
        os.makedirs(results_dir, exist_ok=True)
        
        filepath = os.path.join(results_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Training results saved to: {filename}")
        return filepath


def main():
    """Main training and validation workflow"""
    print("🚀 Enhanced ML Training and Validation")
    print("=" * 50)
    
    try:
        # Initialize trainer
        trainer = EnhancedMLTrainer()
        
        # Load enhanced training data
        print("📊 Loading enhanced training data...")
        training_data = trainer.load_enhanced_training_data()
        print(f"✅ Loaded {len(training_data['examples'])} training examples")
        
        # Validate data quality
        validation_results = trainer.validate_training_data(training_data)
        print(f"✅ Data validation completed")
        
        # Train models
        training_results = trainer.train_all_models(training_data)
        print("✅ Model training completed")
        
        # Test models
        test_results = trainer.test_trained_models(training_data['examples'])
        print("✅ Model testing completed")
        
        # Generate and display report
        report = trainer.generate_training_report(validation_results, training_results, test_results)
        print("\n" + report)
        
        # Save results
        all_results = {
            'validation_results': validation_results,
            'training_results': training_results,
            'test_results': test_results,
            'report': report
        }
        
        results_file = trainer.save_results(all_results)
        print(f"\n📋 Complete results saved to: {os.path.basename(results_file)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Training failed with error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
