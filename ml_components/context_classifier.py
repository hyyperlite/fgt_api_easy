#!/usr/bin/env python3
"""
Endpoint Context Classifier

Classifies FortiGate API endpoints and their response data into categories
to enable intelligent data display and processing.
"""

import os
import json
import pickle
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score


class EndpointContextClassifier:
    """
    Classifies FortiGate API endpoints and data into contextual categories
    for intelligent display and processing.
    """
    
    def __init__(self, model_dir: Optional[str] = None):
        """
        Initialize the classifier
        
        Args:
            model_dir: Directory to save/load trained models
        """
        self.model_dir = model_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'ml_components', 'models'
        )
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words='english'
        )
        self.classifier = MultinomialNB(alpha=0.1)
        
        # Define endpoint categories and their characteristics
        self.categories = {
            'firewall_policy': {
                'keywords': ['policy', 'rule', 'allow', 'deny', 'source', 'destination', 
                           'srcaddr', 'dstaddr', 'srcintf', 'dstintf', 'service', 'action'],
                'endpoints': ['/cmdb/firewall/policy', '/cmdb/firewall/policy6'],
                'fields': ['policyid', 'name', 'srcaddr', 'dstaddr', 'action', 'status']
            },
            'firewall_objects': {
                'keywords': ['address', 'addrgrp', 'service', 'custom', 'group', 'member'],
                'endpoints': ['/cmdb/firewall/address', '/cmdb/firewall/addrgrp', 
                            '/cmdb/firewall/service/custom', '/cmdb/firewall/service/group'],
                'fields': ['name', 'subnet', 'type', 'member', 'comment']
            },
            'routing': {
                'keywords': ['route', 'static', 'gateway', 'interface', 'dst', 'device',
                           'distance', 'router', 'ipv4', 'ipv6'],
                'endpoints': ['/cmdb/router/static', '/monitor/router/ipv4'],
                'fields': ['dst', 'gateway', 'device', 'distance', 'interface']
            },
            'vpn': {
                'keywords': ['vpn', 'ipsec', 'ssl', 'tunnel', 'phase1', 'phase2', 
                           'certificate', 'proposal', 'peer'],
                'endpoints': ['/cmdb/vpn/ipsec/phase1-interface', '/cmdb/vpn/ipsec/phase2-interface',
                            '/monitor/vpn/ipsec'],
                'fields': ['name', 'interface', 'peer', 'proposal', 'status']
            },
            'system': {
                'keywords': ['system', 'status', 'interface', 'resource', 'license', 
                           'version', 'hostname', 'model', 'serial'],
                'endpoints': ['/cmdb/system/interface', '/monitor/system/status', 
                            '/monitor/system/interface'],
                'fields': ['name', 'ip', 'status', 'type', 'version', 'model']
            },
            'user_auth': {
                'keywords': ['user', 'local', 'group', 'auth', 'authentication', 
                           'ldap', 'radius', 'login'],
                'endpoints': ['/cmdb/user/local', '/cmdb/user/group'],
                'fields': ['name', 'status', 'type', 'member']
            },
            'monitor': {
                'keywords': ['monitor', 'status', 'statistics', 'bytes', 'packets',
                           'session', 'traffic', 'performance'],
                'endpoints': ['/monitor/system/status', '/monitor/system/interface'],
                'fields': ['name', 'status', 'rx_bytes', 'tx_bytes']
            }
        }
        
        # Load trained models if they exist
        self._load_models()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def classify_endpoint_data(self, endpoint_path: str, data_content: Any) -> Dict[str, Any]:
        """
        Classify an endpoint and its data content
        
        Args:
            endpoint_path: The API endpoint path
            data_content: The response data from the endpoint
            
        Returns:
            Dict containing classification results
        """
        try:
            # Extract features from endpoint and data
            features = self._extract_features(endpoint_path, data_content)
            
            # If we have a trained model, use it
            if hasattr(self.vectorizer, 'vocabulary_') and hasattr(self.classifier, 'classes_'):
                feature_vector = self.vectorizer.transform([features])
                predicted_category = self.classifier.predict(feature_vector)[0]
                confidence = self.classifier.predict_proba(feature_vector).max()
            else:
                # Fall back to rule-based classification
                predicted_category, confidence = self._rule_based_classify(endpoint_path, data_content)
            
            return {
                'category': predicted_category,
                'confidence': confidence,
                'endpoint': endpoint_path,
                'suggested_fields': self.categories.get(predicted_category, {}).get('fields', []),
                'features_extracted': len(features.split())
            }
            
        except Exception as e:
            self.logger.error(f"Error classifying endpoint {endpoint_path}: {e}")
            return {
                'category': 'unknown',
                'confidence': 0.0,
                'endpoint': endpoint_path,
                'suggested_fields': [],
                'error': str(e)
            }
    
    def _extract_features(self, endpoint: str, data: Any) -> str:
        """
        Extract meaningful features from API endpoint and response data
        
        Args:
            endpoint: API endpoint path
            data: Response data
            
        Returns:
            String of extracted features
        """
        features = []
        
        # Extract from endpoint path
        endpoint_parts = endpoint.lower().split('/')
        features.extend([part for part in endpoint_parts if part])
        
        # Extract from data structure
        if isinstance(data, dict):
            # Single object
            features.extend(data.keys())
            # Add some values that might be informative
            for key, value in data.items():
                if isinstance(value, str) and len(value) < 50:
                    features.append(value.lower())
        elif isinstance(data, list) and data:
            # List of objects - analyze first few items
            for item in data[:3]:  # Only check first 3 items
                if isinstance(item, dict):
                    features.extend(item.keys())
        
        return ' '.join(features)
    
    def _rule_based_classify(self, endpoint: str, data: Any) -> Tuple[str, float]:
        """
        Rule-based classification fallback when no trained model exists
        
        Args:
            endpoint: API endpoint path
            data: Response data
            
        Returns:
            Tuple of (category, confidence)
        """
        endpoint_lower = endpoint.lower()
        
        # Direct endpoint matching
        for category, info in self.categories.items():
            for known_endpoint in info['endpoints']:
                if known_endpoint in endpoint_lower:
                    return category, 0.9
        
        # Keyword matching
        scores = {}
        for category, info in self.categories.items():
            score = 0
            for keyword in info['keywords']:
                if keyword in endpoint_lower:
                    score += 1
            
            # Also check data content if available
            if isinstance(data, dict):
                for keyword in info['keywords']:
                    if any(keyword in str(key).lower() for key in data.keys()):
                        score += 0.5
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                for keyword in info['keywords']:
                    if any(keyword in str(key).lower() for key in data[0].keys()):
                        score += 0.5
            
            if score > 0:
                scores[category] = score
        
        if scores:
            best_category = max(scores, key=scores.get)
            confidence = min(0.8, scores[best_category] / 5)  # Normalize confidence
            return best_category, confidence
        
        return 'unknown', 0.1
    
    def train_model(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train the classification model with provided training data
        
        Args:
            training_data: List of training examples with 'endpoint', 'data', and 'category'
            
        Returns:
            Dict containing training results and metrics
        """
        if not training_data:
            raise ValueError("Training data cannot be empty")
        
        # Prepare training data
        X = []  # Features
        y = []  # Categories
        
        for example in training_data:
            features = self._extract_features(example['endpoint'], example.get('data', {}))
            X.append(features)
            y.append(example['category'])
        
        # Split data for training and validation
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Fit vectorizer and transform features
        X_train_vectorized = self.vectorizer.fit_transform(X_train)
        X_test_vectorized = self.vectorizer.transform(X_test)
        
        # Train classifier
        self.classifier.fit(X_train_vectorized, y_train)
        
        # Evaluate model
        y_pred = self.classifier.predict(X_test_vectorized)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # Save trained models
        self._save_models()
        
        self.logger.info(f"Model trained with accuracy: {accuracy:.3f}")
        
        return {
            'accuracy': accuracy,
            'classification_report': report,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'categories': list(set(y))
        }
    
    def _save_models(self):
        """Save trained models to disk"""
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Save vectorizer
        vectorizer_path = os.path.join(self.model_dir, 'vectorizer.pkl')
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        # Save classifier
        classifier_path = os.path.join(self.model_dir, 'classifier.pkl')
        with open(classifier_path, 'wb') as f:
            pickle.dump(self.classifier, f)
        
        # Save categories
        categories_path = os.path.join(self.model_dir, 'categories.json')
        with open(categories_path, 'w') as f:
            json.dump(self.categories, f, indent=2)
        
        self.logger.info(f"Models saved to {self.model_dir}")
    
    def _load_models(self):
        """Load trained models from disk if they exist"""
        try:
            vectorizer_path = os.path.join(self.model_dir, 'vectorizer.pkl')
            classifier_path = os.path.join(self.model_dir, 'classifier.pkl')
            
            if os.path.exists(vectorizer_path) and os.path.exists(classifier_path):
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                
                with open(classifier_path, 'rb') as f:
                    self.classifier = pickle.load(f)
                
                self.logger.info("Pre-trained models loaded successfully")
            
        except Exception as e:
            self.logger.warning(f"Could not load pre-trained models: {e}")
    
    def get_category_info(self, category: str) -> Dict[str, Any]:
        """Get information about a specific category"""
        return self.categories.get(category, {})
    
    def list_categories(self) -> List[str]:
        """Get list of all available categories"""
        return list(self.categories.keys())


if __name__ == "__main__":
    # Quick test
    classifier = EndpointContextClassifier()
    
    # Test classification
    test_endpoint = "/cmdb/firewall/policy"
    test_data = {"policyid": 1, "name": "test_policy", "srcaddr": "all", "dstaddr": "all"}
    
    result = classifier.classify_endpoint_data(test_endpoint, test_data)
    print(f"Classification result: {result}")
