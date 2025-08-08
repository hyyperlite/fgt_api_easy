#!/usr/bin/env python3
"""
Enhanced ML-Based Intent Classifier for Natural Language Processing

This module uses machine learning models trained on comprehensive natural language
data to understand user intent for formatting, field selection, and filtering.
Replaces rigid regex patterns with robust ML classification.
"""

import os
import json
import pickle
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

# Import the canonical UserIntent dataclass
from .user_intent import UserIntent

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report
    import joblib
except ImportError:
    print("❌ Required ML libraries not found. Installing...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "scikit-learn", "numpy"])
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report
    import joblib


@dataclass
class ClassifierOutput:
    """Internal representation of classification results before creating UserIntent."""
    endpoint: str
    endpoint_confidence: float
    format_type: str
    format_confidence: float
    requested_fields: List[str]
    field_confidence: float
    filter_conditions: List[Dict[str, Any]]
    filter_confidence: float
    output_style: str
    classifications: Dict[str, Any]


class EnhancedMLIntentClassifier:
    """ML-based classifier for understanding user intent in natural language"""
    
    def __init__(self, models_dir: Optional[str] = None):
        self.models_dir = models_dir or os.path.join(os.path.dirname(__file__), 'models')
        os.makedirs(self.models_dir, exist_ok=True)
        
        # ML Models & Encoders
        self.endpoint_model = None
        self.category_model = None
        self.format_model = None
        self.endpoint_encoder = None
        self.category_encoder = None
        self.format_encoder = None
        
        # Fallback patterns for when ML is not available
        self.fallback_patterns = self._build_fallback_patterns()
        
        # Endpoint-specific field mappings for intelligent defaults
        self.endpoint_fields = {
            '/cmdb/firewall/policy': {
                'priority': ['name', 'action', 'srcintf', 'dstintf', 'srcaddr', 'dstaddr', 'service', 'status'],
                'common': ['uuid', 'policyid', 'comments', 'schedule', 'logtraffic'],
                'advanced': ['nat', 'utm-status', 'inspection-mode', 'profile-type']
            },
            '/cmdb/system/interface': {
                'priority': ['name', 'status', 'ip', 'type', 'description'],
                'common': ['mode', 'vdom', 'mtu', 'speed'],
                'advanced': ['vlanid', 'role', 'allowaccess']
            },
            '/cmdb/vpn/ipsec/phase1-interface': {
                'priority': ['name', 'remote-gw', 'status', 'interface', 'proposal'],
                'common': ['mode', 'peertype', 'authmethod'],
                'advanced': ['xauthtype', 'keylife', 'dpd']
            }
        }
        
        # Load models if available
        self._load_trained_models()
    
    def _build_fallback_patterns(self) -> Dict[str, Any]:
        """Build fallback patterns for when ML models aren't available"""
        return {
            'format': {
                'csv': [r'\bcsv\b', r'\bcomma.separated\b'],
                'json': [r'\bjson\b', r'\bjavascript.*object\b'],
                'html': [r'\bhtml\b', r'\bweb.*page\b'],
                'pdf': [r'\bpdf\b', r'\bdocument\b'],
                'table': [r'\btable\b', r'\btabular\b', r'\bput.*in.*table\b', r'\bin.*table.*format\b'],
                'summary': [r'\bsummar[yi]\b', r'\boverview\b']
            },
            'fields': [
                r'\b(?:only|just|show|display)\s+(?:me\s+)?(?:the\s+)?((?:[\w\-]+(?:(?:\s+and\s+|\s*,\s*)[\w\-]+)*))(?:\s+(?:field|column|attribute)s?)?',
                r'\bfields?\s+((?:[\w\-]+(?:(?:\s+and\s+|\s*,\s*)[\w\-]+)*))\b',
                r'\bcolumns?\s+((?:[\w\-]+(?:(?:\s+and\s+|\s*,\s*)[\w\-]+)*))\b'
            ],
            'filters': [
                r'\b(?:where|with|for|having)\s+(.*?)(?:\s+(?:and|or|sort|order|limit)|$)',
                r'\bfilter(?:ed)?\s+(?:by\s+)?(.*?)(?:\s+(?:and|or|sort|order|limit)|$)',
                r'\bcontain(?:ing|s)\s+(.*?)(?:\s+(?:and|or|sort|order|limit)|$)',
                r'\b(enabled|disabled|active|inactive)\s+(?:policies|interfaces|users|rules)\b'
            ]
        }
    
    def _load_trained_models(self):
        """Load trained models and label encoders from disk"""
        self.logger = logging.getLogger(__name__)
        try:
            for model_name in ['endpoint', 'category', 'format']:
                model_path = os.path.join(self.models_dir, f'{model_name}_model.pkl')
                encoder_path = os.path.join(self.models_dir, f'{model_name}_label_encoder.pkl')

                if os.path.exists(model_path) and os.path.exists(encoder_path):
                    with open(model_path, 'rb') as f:
                        setattr(self, f'{model_name}_model', pickle.load(f))
                    with open(encoder_path, 'rb') as f:
                        setattr(self, f'{model_name}_encoder', pickle.load(f))
                    self.logger.info(f"✅ Loaded {model_name} model and encoder.")
                else:
                    self.logger.warning(f"⚠️ {model_name} model or encoder not found.")

            if any([self.endpoint_model, self.category_model, self.format_model]):
                print("✅ Loaded trained ML models")
        except Exception as e:
            self.logger.error(f"❌ Could not load ML models: {e}")

    def classify_intent(self, user_query: str, endpoint: Optional[str] = None) -> UserIntent:
        """Classify user intent using ML models or fallback patterns"""
        query_lower = user_query.lower()

        # Predict endpoint, category, and format
        endpoint_result = self._predict_with_model(user_query, 'endpoint')
        category_result = self._predict_with_model(user_query, 'category')
        format_result = self._predict_with_model(user_query, 'format', fallback_default='table')

        # If an endpoint was passed in, use it as the ground truth
        if endpoint:
            endpoint_result['prediction'] = endpoint
            endpoint_result['confidence'] = 1.0
            endpoint_result['method'] = 'provided'
        
        # Classify field selection intent
        field_result = self._classify_fields_fallback(user_query, endpoint_result['prediction'])
        
        # Classify filter intent
        filter_result = self._classify_filters_fallback(user_query)
        
        # Classify style intent (using patterns for now)
        style_result = self._classify_style(query_lower)
        
        # Calculate overall confidence (simple average for now)
        confidences = [
            endpoint_result['confidence'],
            category_result['confidence'],
            format_result['confidence'],
            field_result['confidence'],
            filter_result['confidence']
        ]
        overall_confidence = sum(confidences) / len(confidences)

        return UserIntent(
            original_query=user_query,
            method="get", # Assuming GET for now, can be enhanced later
            endpoint=endpoint_result['prediction'],
            format_type=format_result['prediction'],
            output_style=style_result['style'],
            requested_fields=field_result['fields'],
            filter_conditions=filter_result['filters'],
            confidence=overall_confidence,
            endpoint_confidence=endpoint_result['confidence'],
            format_confidence=format_result['confidence'],
            field_confidence=field_result['confidence'],
            filter_confidence=filter_result['confidence']
        )

    def _predict_with_model(self, query: str, model_name: str, fallback_default: str = 'unknown') -> Dict[str, Any]:
        """Helper to predict a class using a loaded model."""
        model = getattr(self, f'{model_name}_model')
        encoder = getattr(self, f'{model_name}_encoder')

        if model and encoder:
            try:
                probabilities = model.predict_proba([query])[0]
                max_idx = np.argmax(probabilities)
                prediction = encoder.classes_[max_idx]
                confidence = probabilities[max_idx]
                return {
                    'prediction': prediction,
                    'confidence': float(confidence),
                    'method': 'ml_classification'
                }
            except Exception as e:
                self.logger.error(f"Error predicting with {model_name} model: {e}")

        # Fallback if model not loaded or prediction fails
        return {
            'prediction': fallback_default,
            'confidence': 0.1,
            'method': 'fallback_default'
        }

    def _classify_fields_fallback(self, query: str, endpoint: str) -> Dict[str, Any]:
        """Fallback to regex for field extraction."""
        query_lower = query.lower()
        all_extracted_fields = []

        for pattern in self.fallback_patterns['fields']:
            matches = re.findall(pattern, query_lower)
            for match in matches:
                # The match could be a single string of comma/and separated fields
                fields = re.split(r'\s+and\s+|\s*,\s*', match)
                all_extracted_fields.extend([f.strip() for f in fields if f.strip()])
        
        if all_extracted_fields:
            # Basic confidence: 0.7 if any fields are found via regex
            return {"fields": list(set(all_extracted_fields)), "confidence": 0.7, "method": "regex"}
        
        # If no specific fields are requested, return empty list with low confidence
        return {"fields": [], "confidence": 0.2, "method": "none"}

    def _classify_filters_fallback(self, query: str) -> Dict[str, Any]:
        """Fallback to regex for filter extraction."""
        query_lower = query.lower()
        conditions = []
        confidence = 0.2 # Start with low confidence

        for pattern in self.fallback_patterns['filters']:
            matches = re.findall(pattern, query_lower)
            for match in matches:
                # This is a very basic parser and needs significant improvement
                # It looks for patterns like "field operator value"
                # Clean parts by removing punctuation
                parts = [p.strip(".,;") for p in match.strip().split()]
                if 'status' in parts and 'enable' in parts:
                    conditions.append({"field": "status", "operator": "==", "value": "enable"})
                    confidence = 0.8
                elif 'status' in parts and 'disable' in parts:
                    conditions.append({"field": "status", "operator": "==", "value": "disable"})
                    confidence = 0.8
                elif 'action' in parts and 'accept' in parts:
                    conditions.append({"field": "action", "operator": "==", "value": "accept"})
                    confidence = 0.8
                elif 'action' in parts and 'deny' in parts:
                    conditions.append({"field": "action", "operator": "==", "value": "deny"})
                    confidence = 0.8
                # Add more specific, common cases here
        
        # Handle simple adjective filters like "enabled policies"
        if not conditions:
            if re.search(r'\benabled\b', query_lower):
                conditions.append({"field": "status", "operator": "==", "value": "enable"})
                confidence = 0.75
            elif re.search(r'\bdisabled\b', query_lower):
                conditions.append({"field": "status", "operator": "==", "value": "disable"})
                confidence = 0.75

        return {"filters": conditions, "confidence": confidence, "method": "regex"}
    
    def _classify_style(self, query_lower: str) -> Dict[str, Any]:
        """Classify output style preference"""
        style_patterns = {
            'brief': [r'\bbrief\b', r'\bshort\b', r'\bcompact\b', r'\bquick\b'],
            'detailed': [r'\bdetailed\b', r'\bverbose\b', r'\bfull\b', r'\bcomplete\b'],
            'minimal': [r'\bminimal\b', r'\bbasic\b', r'\bsimple\b', r'\bclean\b']
        }
        
        for style, patterns in style_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    return {'style': style, 'confidence': 0.8}
        
        return {'style': 'standard', 'confidence': 0.4}


# Singleton instance
_enhanced_intent_classifier = None

def get_enhanced_intent_classifier() -> EnhancedMLIntentClassifier:
    """Get singleton instance of the enhanced intent classifier"""
    global _enhanced_intent_classifier
    if _enhanced_intent_classifier is None:
        _enhanced_intent_classifier = EnhancedMLIntentClassifier()
    return _enhanced_intent_classifier


def classify_user_intent(user_query: str, endpoint: Optional[str] = None) -> UserIntent:
    """Main function to classify user intent from natural language using enhanced ML"""
    classifier = get_enhanced_intent_classifier()
    return classifier.classify_intent(user_query, endpoint)


def train_enhanced_models(training_data_path: Optional[str] = None) -> Dict[str, Any]:
    """Train the enhanced ML models with robust training data"""
    # This function is now a proxy to the main training script.
    # The classifier class itself no longer holds training logic.
    print("Triggering main training script...")
    # In a real application, you might use subprocess to call train_enhanced_models.py
    # For now, we'll just print a message.
    return {"status": "Training should be done via train_enhanced_models.py script."}


if __name__ == "__main__":
    # Test the enhanced ML intent classifier
    print("🤖 Testing Enhanced ML Intent Classifier")
    print("=" * 50)
    
    # The classifier now loads pre-trained models.
    # Ensure you have run `python3 train_enhanced_models.py` first.
    
    # Test queries with many variations
    test_queries = [
        # Format variations
        ("show me firewall policies and format as pdf", "/cmdb/firewall/policy"),
        ("display interfaces in json format", "/cmdb/system/interface"),
        
        # Field variations  
        ("show me just name and action for policies", "/cmdb/firewall/policy"),
        ("display only the status and ip fields for interfaces", "/cmdb/system/interface"),
        
        # Filter variations
        ("show only enabled policies", "/cmdb/firewall/policy"),
        ("display interfaces where status is up", "/cmdb/system/interface"),
        ("get policies with name contains 'guest'", "/cmdb/firewall/policy"),
        
        # Combined variations
        ("show enabled policies with name and action in csv format", "/cmdb/firewall/policy"),
        ("display active interfaces where type is vlan and format as json", None),
        ("give me just the names of allowed policies as a table", "/cmdb/firewall/policy")
    ]
    
    classifier = get_enhanced_intent_classifier()
    
    for query, endpoint in test_queries:
        print(f"\n🔤 Query: '{query}'")
        if endpoint:
            print(f"📍 Endpoint (provided): {endpoint}")
        print("-" * 60)
        
        intent = classifier.classify_intent(query, endpoint)
        
        print(f"  - Endpoint: {intent.endpoint} (confidence: {intent.endpoint_confidence:.2f})")
        print(f"  - Format: {intent.format_type} (confidence: {intent.format_confidence:.2f})")
        print(f"  - Fields: {intent.requested_fields} (confidence: {intent.field_confidence:.2f})")
        print(f"  - Filters: {intent.filter_conditions} (confidence: {intent.filter_confidence:.2f})")
        print(f"  - Style: {intent.output_style}")
        print(f"  - Overall Confidence: {intent.confidence:.2f}")
