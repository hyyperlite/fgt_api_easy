#!/usr/bin/env python3
"""
Enhanced ML-Based Intent Classifier for Natural Language Processing

This m        # Fallback patterns for when ML is not available
        self.fallback_patterns = {
            'format': {
                'csv': [r'\bcsv\b', r'\bcomma.separated\b', r'\bexport.*csv\b'],
                'json': [r'\bjson\b', r'\bjavascript.*object\b', r'\bexport.*json\b'],
                'html': [r'\bhtml\b', r'\bweb.*page\b', r'\bhtml.*table\b'],
                'table': [r'\btable\b', r'\btabular\b', r'\bput.*table\b', r'\bin.*table.*format\b'],
                'summary': [r'\bsummar[yi]\b', r'\boverview\b']
            },
            'fields': [
                r'\b(?:only|just|show|display)\s+(?:me\s+)?(?:the\s+)?((?:\w+(?:\s+and\s+|\s*,\s*)?)+?)(?:\s+(?:field|column|attribute)s?)?\s*(?:for|from|$)',
                r'\bfields?\s+((?:\w+(?:\s+and\s+|\s*,\s*)?)+)\b',
                r'\bcolumns?\s+((?:\w+(?:\s+and\s+|\s*,\s*)?)+)\b',
                r'\bshow\s+(?:me\s+)?(?:just\s+|only\s+)?((?:\w+(?:\s+and\s+|\s*,\s*)?)+)(?:\s+for|\s+from|\s*$)'
            ],
            'filters': [
                r'\b(?:where|with|having)\s+(.*?)(?:\s+(?:from|for)|\s*$)',
                r'\bfilter(?:ed)?\s+(?:by\s+)?(.*?)(?:\s+(?:from|for)|\s*$)',
                r'\bcontain(?:ing|s)\s+(.*?)(?:\s+(?:from|for)|\s*$)',
                r'\bshow\s+(?:only\s+)?(enabled|disabled|active|inactive)(?:\s+|$)',
                r'\b(enabled|disabled|active|inactive)\s+(?:only|policies|interfaces|connections)(?:\s+|$)'
            ]
        }earning models trained on comprehensive natural language
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
class UserIntent:
    """Represents the user's parsed intent from natural language"""
    format_type: str  # csv, html, json, table, summary, list, etc.
    format_confidence: float
    
    requested_fields: List[str]  # specific fields user wants to see
    field_confidence: float
    
    filter_conditions: List[str]  # filtering criteria
    filter_confidence: float
    
    output_style: str  # brief, detailed, compact, etc.
    
    # Raw classifications for debugging
    classifications: Dict[str, Any]


class EnhancedMLIntentClassifier:
    """ML-based classifier for understanding user intent in natural language"""
    
    def __init__(self, models_dir: str = None):
        self.models_dir = models_dir or os.path.join(os.path.dirname(__file__), 'models')
        os.makedirs(self.models_dir, exist_ok=True)
        
        # ML Models
        self.format_classifier = None
        self.field_extractor = None
        self.filter_extractor = None
        
        # Feature extractors
        self.format_vectorizer = None
        self.field_vectorizer = None
        self.filter_vectorizer = None
        
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
    
    def _build_fallback_patterns(self) -> Dict[str, List[str]]:
        """Build fallback patterns for when ML models aren't available"""
        return {
            'format': {
                'csv': [r'\bcsv\b', r'\bcomma.separated\b'],
                'json': [r'\bjson\b', r'\bjavascript.*object\b'],
                'html': [r'\bhtml\b', r'\bweb.*page\b'],
                'table': [r'\btable\b', r'\btabular\b', r'\bput.*in.*table\b', r'\bin.*table.*format\b'],
                'summary': [r'\bsummar[yi]\b', r'\boverview\b']
            },
            'fields': [
                r'\b(?:only|just|show|display)\s+(?:me\s+)?(?:the\s+)?([\w\s,]+?)(?:\s+(?:field|column|attribute)s?)?\b',
                r'\bfields?\s+([\w\s,]+)\b',
                r'\bcolumns?\s+([\w\s,]+)\b'
            ],
            'filters': [
                r'\b(?:where|with|having)\s+(.*?)(?:\s+(?:from|for)|\s*$)',
                r'\bfilter(?:ed)?\s+(?:by\s+)?(.*?)(?:\s+(?:from|for)|\s*$)',
                r'\bcontain(?:ing|s)\s+(.*?)(?:\s+(?:from|for)|\s*$)'
            ]
        }
    
    def train_models(self, training_data_path: str = None) -> Dict[str, Any]:
        """Train ML models using the robust training data"""
        print("🤖 Training enhanced ML intent classification models...")
        
        # Load training data
        if not training_data_path:
            training_data_path = self._find_latest_training_data()
        
        if not training_data_path or not os.path.exists(training_data_path):
            print("❌ No training data found. Using fallback patterns only.")
            return {'status': 'fallback_only', 'error': 'No training data available'}
        
        with open(training_data_path, 'r') as f:
            training_data = json.load(f)
        
        examples = training_data['examples']
        print(f"   📊 Loading {len(examples)} training examples...")
        
        results = {}
        
        # Train format classifier
        print("   🎯 Training format classifier...")
        format_result = self._train_format_classifier(examples)
        results['format_classifier'] = format_result
        
        # Train field extractor  
        print("   📋 Training field extractor...")
        field_result = self._train_field_extractor(examples)
        results['field_extractor'] = field_result
        
        # Train filter extractor
        print("   🔍 Training filter extractor...")
        filter_result = self._train_filter_extractor(examples)
        results['filter_extractor'] = filter_result
        
        # Save models
        self._save_trained_models()
        
        print("   ✅ ML model training completed!")
        return results
    
    def _train_format_classifier(self, examples: List[Dict]) -> Dict[str, Any]:
        """Train the format classification model"""
        # Extract format examples
        format_examples = [ex for ex in examples if 'format' in ex and ex.get('intent_type') in ['format', 'combined']]
        
        if len(format_examples) < 50:
            return {'status': 'insufficient_data', 'count': len(format_examples)}
        
        # Prepare training data
        texts = [ex['text'] for ex in format_examples]
        labels = [ex['format'] for ex in format_examples]
        
        # Create pipeline with TF-IDF and Random Forest
        self.format_vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 3),
            stop_words='english',
            lowercase=True
        )
        
        self.format_classifier = Pipeline([
            ('tfidf', self.format_vectorizer),
            ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
        ])
        
        # Split and train
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        self.format_classifier.fit(X_train, y_train)
        
        # Evaluate
        train_score = self.format_classifier.score(X_train, y_train)
        test_score = self.format_classifier.score(X_test, y_test)
        
        return {
            'status': 'trained',
            'examples_count': len(format_examples),
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'unique_formats': len(set(labels))
        }
    
    def _train_field_extractor(self, examples: List[Dict]) -> Dict[str, Any]:
        """Train the field extraction model"""
        # Extract field examples and also add some negative examples
        field_examples = [ex for ex in examples if 'requested_fields' in ex and ex.get('intent_type') in ['fields', 'combined']]
        
        # Add some negative examples (format/filter only examples)
        negative_examples = [ex for ex in examples if ex.get('intent_type') in ['format', 'filter'] and 'requested_fields' not in ex][:len(field_examples)//2]
        
        all_examples = field_examples + negative_examples
        
        if len(all_examples) < 50:
            return {'status': 'insufficient_data', 'count': len(all_examples)}
        
        # For field extraction, we'll use a hybrid approach:
        # ML to detect if fields are requested, then extract using patterns
        texts = [ex['text'] for ex in all_examples]
        # Binary classification: contains field request or not
        labels = [1 if ex.get('requested_fields') else 0 for ex in all_examples]
        
        self.field_extractor = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=500, ngram_range=(1, 2))),
            ('classifier', LogisticRegression(random_state=42))
        ])
        
        # Split and train
        if len(set(labels)) < 2:
            # All examples have the same label, create a simple classifier
            return {
                'status': 'single_class',
                'examples_count': len(all_examples),
                'class_label': labels[0] if labels else 0,
                'train_accuracy': 1.0,
                'test_accuracy': 1.0
            }
            
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42
        )
        
        self.field_extractor.fit(X_train, y_train)
        
        train_score = self.field_extractor.score(X_train, y_train)
        test_score = self.field_extractor.score(X_test, y_test)
        
        return {
            'status': 'trained',
            'examples_count': len(all_examples),
            'positive_examples': len(field_examples),
            'negative_examples': len(negative_examples),
            'train_accuracy': train_score,
            'test_accuracy': test_score
        }
    
    def _train_filter_extractor(self, examples: List[Dict]) -> Dict[str, Any]:
        """Train the filter extraction model"""
        # Extract filter examples and add negative examples
        filter_examples = [ex for ex in examples if 'filter_condition' in ex and ex.get('intent_type') in ['filter', 'combined']]
        
        # Add some negative examples (format/field only examples)
        negative_examples = [ex for ex in examples if ex.get('intent_type') in ['format', 'fields'] and 'filter_condition' not in ex][:len(filter_examples)//2]
        
        all_examples = filter_examples + negative_examples
        
        if len(all_examples) < 50:
            return {'status': 'insufficient_data', 'count': len(all_examples)}
        
        # Binary classification: contains filter request or not
        texts = [ex['text'] for ex in all_examples]
        labels = [1 if ex.get('filter_condition') else 0 for ex in all_examples]
        
        self.filter_extractor = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=500, ngram_range=(1, 2))),
            ('classifier', LogisticRegression(random_state=42))
        ])
        
        # Split and train
        if len(set(labels)) < 2:
            # All examples have the same label, create a simple classifier
            return {
                'status': 'single_class',
                'examples_count': len(all_examples),
                'class_label': labels[0] if labels else 0,
                'train_accuracy': 1.0,
                'test_accuracy': 1.0
            }
            
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42
        )
        
        self.filter_extractor.fit(X_train, y_train)
        
        train_score = self.filter_extractor.score(X_train, y_train)
        test_score = self.filter_extractor.score(X_test, y_test)
        
        return {
            'status': 'trained',
            'examples_count': len(all_examples),
            'positive_examples': len(filter_examples),
            'negative_examples': len(negative_examples),
            'train_accuracy': train_score,
            'test_accuracy': test_score
        }
    
    def _save_trained_models(self):
        """Save trained models to disk"""
        try:
            if self.format_classifier:
                joblib.dump(self.format_classifier, os.path.join(self.models_dir, 'format_classifier.pkl'))
            
            if self.field_extractor:
                joblib.dump(self.field_extractor, os.path.join(self.models_dir, 'field_extractor.pkl'))
            
            if self.filter_extractor:
                joblib.dump(self.filter_extractor, os.path.join(self.models_dir, 'filter_extractor.pkl'))
            
            print("💾 ML models saved successfully")
        except Exception as e:
            print(f"❌ Error saving models: {e}")
    
    def _load_trained_models(self):
        """Load trained models from disk"""
        try:
            format_path = os.path.join(self.models_dir, 'format_classifier.pkl')
            if os.path.exists(format_path):
                self.format_classifier = joblib.load(format_path)
            
            field_path = os.path.join(self.models_dir, 'field_extractor.pkl')
            if os.path.exists(field_path):
                self.field_extractor = joblib.load(field_path)
            
            filter_path = os.path.join(self.models_dir, 'filter_extractor.pkl')
            if os.path.exists(filter_path):
                self.filter_extractor = joblib.load(filter_path)
                
            if any([self.format_classifier, self.field_extractor, self.filter_extractor]):
                print("✅ Loaded trained ML models")
        except Exception as e:
            print(f"⚠️  Could not load ML models: {e}")
    
    def _find_latest_training_data(self) -> str:
        """Find the most recent training data file"""
        training_dir = os.path.join(os.path.dirname(__file__), 'training_data')
        if not os.path.exists(training_dir):
            return None
        
        # Look for robust training data first
        files = [f for f in os.listdir(training_dir) if f.startswith('robust_nl_training_data_')]
        if not files:
            # Fallback to enhanced training data
            files = [f for f in os.listdir(training_dir) if f.startswith('enhanced_training_data_')]
        
        if not files:
            return None
        
        # Get most recent
        files.sort(reverse=True)
        return os.path.join(training_dir, files[0])
    
    def classify_intent(self, user_query: str, endpoint: str = None) -> UserIntent:
        """Classify user intent using ML models or fallback patterns"""
        query_lower = user_query.lower()
        
        # Classify format intent
        format_result = self._classify_format_ml(user_query) if self.format_classifier else self._classify_format_fallback(query_lower)
        
        # Classify field selection intent
        field_result = self._classify_fields_ml(user_query, endpoint) if self.field_extractor else self._classify_fields_fallback(user_query, endpoint)
        
        # Classify filter intent
        filter_result = self._classify_filters_ml(user_query) if self.filter_extractor else self._classify_filters_fallback(user_query)
        
        # Classify style intent (using patterns for now)
        style_result = self._classify_style(query_lower)
        
        return UserIntent(
            format_type=format_result['format'],
            format_confidence=format_result['confidence'],
            requested_fields=field_result['fields'],
            field_confidence=field_result['confidence'],
            filter_conditions=filter_result['filters'],
            filter_confidence=filter_result['confidence'],
            output_style=style_result['style'],
            classifications={
                'format': format_result,
                'fields': field_result,
                'filters': filter_result,
                'style': style_result
            }
        )
    
    def _classify_format_ml(self, user_query: str) -> Dict[str, Any]:
        """Use ML model to classify format intent with pattern override"""
        try:
            # Get prediction probabilities
            probabilities = self.format_classifier.predict_proba([user_query])[0]
            classes = self.format_classifier.classes_
            
            # Get the most confident prediction
            max_idx = np.argmax(probabilities)
            predicted_format = classes[max_idx]
            confidence = probabilities[max_idx]
            
            # Check if we have a strong pattern match that should override
            pattern_result = self._classify_format_fallback(user_query.lower())
            
            # If ML confidence is low or pattern has high confidence, prefer pattern
            if (confidence < 0.7 and pattern_result['confidence'] > 0.6) or \
               (pattern_result['confidence'] > 0.8):
                return pattern_result
            
            return {
                'format': predicted_format,
                'confidence': float(confidence),
                'method': 'ml_classification',
                'all_probabilities': {cls: float(prob) for cls, prob in zip(classes, probabilities)}
            }
        except Exception as e:
            # Fallback to pattern matching
            return self._classify_format_fallback(user_query.lower())
    
    def _classify_format_fallback(self, query_lower: str) -> Dict[str, Any]:
        """Fallback format classification using patterns"""
        format_scores = {}
        
        for format_type, patterns in self.fallback_patterns['format'].items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    score += 1
            
            if score > 0:
                format_scores[format_type] = score
        
        if not format_scores:
            return {'format': 'table', 'confidence': 0.4, 'method': 'default'}
        
        best_format = max(format_scores.items(), key=lambda x: x[1])
        confidence = min(0.95, 0.5 + (best_format[1] * 0.15))
        
        return {
            'format': best_format[0],
            'confidence': confidence,
            'method': 'pattern_fallback'
        }
    
    def _classify_fields_ml(self, user_query: str, endpoint: str = None) -> Dict[str, Any]:
        """Use ML model to detect and extract field requests"""
        try:
            # Check if query contains field request
            has_fields_prob = self.field_extractor.predict_proba([user_query])[0][1]
            
            if has_fields_prob > 0.5:
                # Extract fields using pattern matching (hybrid approach)
                return self._extract_fields_from_query(user_query, endpoint, has_fields_prob)
            else:
                # Use intelligent defaults
                return self._get_intelligent_field_defaults(user_query, endpoint, has_fields_prob)
                
        except Exception as e:
            return self._classify_fields_fallback(user_query, endpoint)
    
    def _classify_fields_fallback(self, user_query: str, endpoint: str = None) -> Dict[str, Any]:
        """Fallback field classification using patterns"""
        return self._extract_fields_from_query(user_query, endpoint, 0.6)
    
    def _extract_fields_from_query(self, user_query: str, endpoint: str = None, confidence: float = 0.8) -> Dict[str, Any]:
        """Extract specific field requests from query"""
        requested_fields = []
        
        # Try to extract specific field requests using improved patterns
        for pattern in self.fallback_patterns['fields']:
            match = re.search(pattern, user_query, re.IGNORECASE)
            if match:
                fields_text = match.group(1)
                # Parse field names more carefully
                fields = []
                
                # Handle "and" and comma separation
                field_parts = re.split(r'\s+and\s+|\s*,\s*', fields_text)
                for part in field_parts:
                    part = part.strip()
                    # Filter out common non-field words
                    if part and part not in ['from', 'for', 'the', 'and', 'or', 'in', 'on', 'at', 'to', 'with', 'just', 'only', 'show', 'display', 'me']:
                        # Check if it's a reasonable field name (alphanumeric, dash, underscore)
                        if re.match(r'^[\w\-]+$', part):
                            fields.append(part)
                
                if fields:
                    requested_fields.extend(fields)
                    break
        
        if requested_fields:
            return {
                'fields': requested_fields,
                'confidence': confidence,
                'method': 'improved_pattern_extraction'
            }
        else:
            return self._get_intelligent_field_defaults(user_query, endpoint, confidence * 0.7)
    
    def _get_intelligent_field_defaults(self, user_query: str, endpoint: str = None, base_confidence: float = 0.5) -> Dict[str, Any]:
        """Get intelligent field defaults based on endpoint and query context"""
        if not endpoint or endpoint not in self.endpoint_fields:
            return {'fields': [], 'confidence': 0.3, 'method': 'no_defaults'}
        
        query_lower = user_query.lower()
        
        # Determine detail level based on query
        if any(word in query_lower for word in ['brief', 'summary', 'quick', 'names']):
            fields = self.endpoint_fields[endpoint]['priority'][:3]
            confidence = base_confidence + 0.1
        elif any(word in query_lower for word in ['detailed', 'full', 'complete', 'all']):
            fields = (self.endpoint_fields[endpoint]['priority'] + 
                     self.endpoint_fields[endpoint]['common'])
            confidence = base_confidence + 0.2
        else:
            fields = self.endpoint_fields[endpoint]['priority']
            confidence = base_confidence
        
        return {
            'fields': fields,
            'confidence': confidence,
            'method': 'intelligent_defaults',
            'endpoint': endpoint
        }
    
    def _classify_filters_ml(self, user_query: str) -> Dict[str, Any]:
        """Use ML model to detect and extract filter requests"""
        try:
            has_filter_prob = self.filter_extractor.predict_proba([user_query])[0][1]
            
            if has_filter_prob > 0.5:
                return self._extract_filters_from_query(user_query, has_filter_prob)
            else:
                return {'filters': [], 'confidence': 0.2, 'method': 'no_filters_detected'}
                
        except Exception as e:
            return self._classify_filters_fallback(user_query)
    
    def _classify_filters_fallback(self, user_query: str) -> Dict[str, Any]:
        """Fallback filter classification using patterns"""
        return self._extract_filters_from_query(user_query, 0.6)
    
    def _extract_filters_from_query(self, user_query: str, confidence: float = 0.7) -> Dict[str, Any]:
        """Extract filter conditions from query"""
        filters = []
        
        for pattern in self.fallback_patterns['filters']:
            match = re.search(pattern, user_query, re.IGNORECASE)
            if match:
                filter_text = match.group(1).strip()
                if filter_text and len(filter_text) > 2:
                    filters.append(filter_text)
                    break
        
        return {
            'filters': filters,
            'confidence': confidence if filters else 0.1,
            'method': 'pattern_extraction'
        }
    
    def _classify_style(self, query_lower: str) -> Dict[str, str]:
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


def classify_user_intent(user_query: str, endpoint: str = None) -> UserIntent:
    """Main function to classify user intent from natural language using enhanced ML"""
    classifier = get_enhanced_intent_classifier()
    return classifier.classify_intent(user_query, endpoint)


def train_enhanced_models(training_data_path: str = None) -> Dict[str, Any]:
    """Train the enhanced ML models with robust training data"""
    classifier = get_enhanced_intent_classifier()
    return classifier.train_models(training_data_path)


if __name__ == "__main__":
    # Test the enhanced ML intent classifier
    print("🤖 Testing Enhanced ML Intent Classifier")
    print("=" * 50)
    
    # First try to train models
    print("📚 Training models with robust training data...")
    train_results = train_enhanced_models()
    print(f"Training results: {train_results}")
    
    # Test queries with many variations
    test_queries = [
        # Format variations
        ("show me firewall policies and format as csv", "/cmdb/firewall/policy"),
        ("display interfaces in json format", "/cmdb/system/interface"),
        ("give me the policies and export to csv", "/cmdb/firewall/policy"),
        ("show interfaces and make it html", "/cmdb/system/interface"),
        ("put the data in table format", None),
        ("convert to json", None),
        ("I want csv output", None),
        
        # Field variations  
        ("show me just name and action for policies", "/cmdb/firewall/policy"),
        ("display only the status and ip fields", "/cmdb/system/interface"),
        ("I need the name, remote-gw, and status attributes", "/cmdb/vpn/ipsec/phase1-interface"),
        ("give me name and action only", "/cmdb/firewall/policy"),
        ("just show the interface names", "/cmdb/system/interface"),
        
        # Filter variations
        ("show only enabled policies", "/cmdb/firewall/policy"),
        ("display interfaces where status is up", "/cmdb/system/interface"),
        ("get policies that have action allow", "/cmdb/firewall/policy"),
        ("filter for active connections", "/cmdb/vpn/ipsec/phase1-interface"),
        
        # Combined variations
        ("show enabled policies with name and action in csv format", "/cmdb/firewall/policy"),
        ("display active interfaces and format as json", "/cmdb/system/interface"),
        ("give me just the names of allowed policies as a table", "/cmdb/firewall/policy")
    ]
    
    classifier = get_enhanced_intent_classifier()
    
    for query, endpoint in test_queries:
        print(f"\n🔤 Query: {query}")
        print(f"📍 Endpoint: {endpoint}")
        print("-" * 60)
        
        intent = classifier.classify_intent(query, endpoint)
        
        print(f"🎯 Format: {intent.format_type} (confidence: {intent.format_confidence:.2f})")
        print(f"📋 Fields: {intent.requested_fields} (confidence: {intent.field_confidence:.2f})")
        print(f"🔍 Filters: {intent.filter_conditions} (confidence: {intent.filter_confidence:.2f})")
        print(f"🎨 Style: {intent.output_style}")
        
        # Show method used
        methods = []
        for key, classification in intent.classifications.items():
            if 'method' in classification:
                methods.append(f"{key}:{classification['method']}")
        print(f"🔧 Methods: {', '.join(methods)}")
