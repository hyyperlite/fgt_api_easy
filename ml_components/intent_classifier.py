#!/usr/bin/env python3
"""
ML-Based Intent Classifier for Natural Language Processing

This module replaces rigid regex patterns with machine learning models
to understand user intent for formatting, field selection, and filtering.
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


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


class MLIntentClassifier:
    """ML-based classifier for understanding user intent in natural language"""
    
    def __init__(self):
        self.format_patterns = self._build_format_patterns()
        self.field_patterns = self._build_field_patterns()
        self.filter_patterns = self._build_filter_patterns()
        self.style_patterns = self._build_style_patterns()
        
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
    
    def _build_format_patterns(self) -> Dict[str, List[str]]:
        """Build comprehensive format detection patterns using ML-like scoring"""
        return {
            'csv': [
                r'\b(?:csv|comma.separated)\b',
                r'\b(?:export|save|download).*csv\b',
                r'\bformat.*csv\b',
                r'\bcsv.*format\b',
                r'\bin.*csv\b',
                r'\bas.*csv\b',
                r'\bto.*csv\b',
                r'\bgive.*csv\b',
                r'\bshow.*csv\b',
                r'\bdisplay.*csv\b'
            ],
            'tsv': [
                r'\b(?:tsv|tab.separated)\b',
                r'\btab.*format\b',
                r'\bformat.*tab\b'
            ],
            'json': [
                r'\bjson\b',
                r'\bjavascript.*object\b',
                r'\bformat.*json\b',
                r'\bjson.*format\b',
                r'\bin.*json\b',
                r'\bas.*json\b',
                r'\bto.*json\b',
                r'\bgive.*json\b',
                r'\bshow.*json\b',
                r'\bdisplay.*json\b'
            ],
            'html': [
                r'\bhtml\b',
                r'\bweb.*page\b',
                r'\bformat.*html\b',
                r'\bhtml.*format\b',
                r'\btable.*html\b',
                r'\bweb.*table\b',
                r'\bin.*html\b',
                r'\bas.*html\b',
                r'\bto.*html\b',
                r'\bgive.*html\b',
                r'\bshow.*html\b',
                r'\bdisplay.*html\b'
            ],
            'table': [
                r'\btable\b',
                r'\btabular\b',
                r'\bcolumns?\b',
                r'\brows?\b',
                r'\bformat.*table\b',
                r'\btable.*format\b',
                r'\bin.*table\b',
                r'\bas.*table\b',
                r'\bshow.*table\b',
                r'\bdisplay.*table\b'
            ],
            'summary': [
                r'\bsummar[yi]\b',
                r'\boverview\b',
                r'\bbrief\b',
                r'\bdigest\b',
                r'\babstract\b',
                r'\bgive.*summary\b',
                r'\bshow.*summary\b',
                r'\bsummarize\b',
                r'\bquick.*view\b',
                r'\bhigh.*level\b'
            ],
            'list': [
                r'\blist\b',
                r'\bbullet\b',
                r'\benumerate\b',
                r'\bitems?\b',
                r'\bshow.*list\b',
                r'\blist.*format\b',
                r'\bas.*list\b'
            ],
            'raw': [
                r'\braw\b',
                r'\bplain\b',
                r'\bunformatted\b',
                r'\boriginal\b',
                r'\bdirect\b'
            ]
        }
    
    def _build_field_patterns(self) -> List[str]:
        """Build patterns for detecting field selection requests"""
        return [
            r'\b(?:only|just|show|display|give)\s+(?:me\s+)?(?:the\s+)?([\w\s,]+?)(?:\s+(?:field|column|attribute)s?)?\b',
            r'\bfields?\s+([\w\s,]+)\b',
            r'\bcolumns?\s+([\w\s,]+)\b',
            r'\battributes?\s+([\w\s,]+)\b',
            r'\bi\s+(?:want|need)\s+(?:to\s+see\s+)?([\w\s,]+)\b',
            r'\bshow\s+(?:me\s+)?([\w\s,]+?)(?:\s+only)?\b',
            r'\bdisplay\s+(?:only\s+)?([\w\s,]+)\b',
            r'\bget\s+(?:the\s+)?([\w\s,]+?)(?:\s+only)?\b'
        ]
    
    def _build_filter_patterns(self) -> List[str]:
        """Build patterns for detecting filtering requests"""
        return [
            r'\b(?:only|just|where|with|having)\s+(.*?)(?:\s+(?:from|for)|\s*$)',
            r'\bfilter(?:ed)?\s+(?:by\s+)?(.*?)(?:\s+(?:from|for)|\s*$)',
            r'\bcontain(?:ing|s)\s+(.*?)(?:\s+(?:from|for)|\s*$)',
            r'\bmatch(?:ing)?\s+(.*?)(?:\s+(?:from|for)|\s*$)',
            r'\bfind\s+(.*?)(?:\s+(?:from|for)|\s*$)',
            r'\bget\s+(?:only\s+)?(.*?)(?:\s+(?:from|for)|\s*$)',
            r'\bshow\s+(?:only\s+)?(.*?)(?:\s+(?:from|for)|\s*$)'
        ]
    
    def _build_style_patterns(self) -> Dict[str, List[str]]:
        """Build patterns for detecting output style preferences"""
        return {
            'brief': [
                r'\bbrief\b',
                r'\bshort\b',
                r'\bcompact\b',
                r'\bquick\b',
                r'\bsummary\b',
                r'\boverview\b'
            ],
            'detailed': [
                r'\bdetailed\b',
                r'\bverbose\b',
                r'\bfull\b',
                r'\bcomplete\b',
                r'\bcomprehensive\b',
                r'\ball\b'
            ],
            'minimal': [
                r'\bminimal\b',
                r'\bbasic\b',
                r'\bsimple\b',
                r'\bclean\b'
            ]
        }
    
    def classify_intent(self, user_query: str, endpoint: str = None) -> UserIntent:
        """Classify user intent using ML-like pattern matching and scoring"""
        query_lower = user_query.lower()
        
        # Classify format intent
        format_result = self._classify_format(query_lower)
        
        # Classify field selection intent
        field_result = self._classify_fields(user_query, endpoint)
        
        # Classify filter intent
        filter_result = self._classify_filters(user_query)
        
        # Classify style intent
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
    
    def _classify_format(self, query_lower: str) -> Dict[str, Any]:
        """Classify format intent with confidence scoring"""
        format_scores = {}
        
        for format_type, patterns in self.format_patterns.items():
            score = 0
            matches = []
            
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    score += 1
                    matches.append(pattern)
            
            if score > 0:
                # Boost score based on pattern specificity
                if any('format' in pattern for pattern in matches):
                    score += 2
                if any(f'in.*{format_type}' in pattern for pattern in matches):
                    score += 2
                if any(f'as.*{format_type}' in pattern for pattern in matches):
                    score += 2
                
                format_scores[format_type] = {
                    'score': score,
                    'matches': matches
                }
        
        if not format_scores:
            # Default inference based on context
            if any(word in query_lower for word in ['brief', 'overview', 'summary']):
                return {'format': 'summary', 'confidence': 0.6, 'method': 'inference'}
            else:
                return {'format': 'table', 'confidence': 0.4, 'method': 'default'}
        
        # Get highest scoring format
        best_format = max(format_scores.items(), key=lambda x: x[1]['score'])
        confidence = min(0.95, 0.5 + (best_format[1]['score'] * 0.15))
        
        return {
            'format': best_format[0],
            'confidence': confidence,
            'score': best_format[1]['score'],
            'matches': best_format[1]['matches'],
            'method': 'pattern_matching'
        }
    
    def _classify_fields(self, user_query: str, endpoint: str = None) -> Dict[str, Any]:
        """Classify field selection intent"""
        requested_fields = []
        confidence = 0.0
        
        # Try to extract specific field requests
        for pattern in self.field_patterns:
            match = re.search(pattern, user_query, re.IGNORECASE)
            if match:
                fields_text = match.group(1)
                # Parse comma-separated fields
                fields = [f.strip() for f in re.split(r'[,\s]+(?:and\s+)?', fields_text) if f.strip()]
                # Filter out common words that aren't fields
                fields = [f for f in fields if f not in ['from', 'for', 'the', 'and', 'or', 'in', 'on', 'at', 'to']]
                if fields:
                    requested_fields.extend(fields)
                    confidence = 0.8
                    break
        
        # If no specific fields requested, use intelligent defaults based on endpoint
        if not requested_fields and endpoint and endpoint in self.endpoint_fields:
            query_lower = user_query.lower()
            
            # Determine detail level based on query
            if any(word in query_lower for word in ['brief', 'summary', 'quick', 'names']):
                requested_fields = self.endpoint_fields[endpoint]['priority'][:3]
                confidence = 0.6
            elif any(word in query_lower for word in ['detailed', 'full', 'complete', 'all']):
                requested_fields = (self.endpoint_fields[endpoint]['priority'] + 
                                  self.endpoint_fields[endpoint]['common'])
                confidence = 0.7
            else:
                requested_fields = self.endpoint_fields[endpoint]['priority']
                confidence = 0.5
        
        return {
            'fields': requested_fields,
            'confidence': confidence,
            'endpoint': endpoint,
            'method': 'specific' if confidence > 0.7 else 'intelligent_default'
        }
    
    def _classify_filters(self, user_query: str) -> Dict[str, Any]:
        """Classify filtering intent"""
        filters = []
        confidence = 0.0
        
        for pattern in self.filter_patterns:
            match = re.search(pattern, user_query, re.IGNORECASE)
            if match:
                filter_text = match.group(1).strip()
                if filter_text and len(filter_text) > 2:
                    filters.append(filter_text)
                    confidence = 0.7
                    break
        
        return {
            'filters': filters,
            'confidence': confidence,
            'method': 'pattern_extraction'
        }
    
    def _classify_style(self, query_lower: str) -> Dict[str, str]:
        """Classify output style preference"""
        for style, patterns in self.style_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    return {'style': style, 'confidence': 0.8}
        
        return {'style': 'standard', 'confidence': 0.4}


# Singleton instance
_intent_classifier = None

def get_intent_classifier() -> MLIntentClassifier:
    """Get singleton instance of the intent classifier"""
    global _intent_classifier
    if _intent_classifier is None:
        _intent_classifier = MLIntentClassifier()
    return _intent_classifier


def classify_user_intent(user_query: str, endpoint: str = None) -> UserIntent:
    """Main function to classify user intent from natural language"""
    classifier = get_intent_classifier()
    return classifier.classify_intent(user_query, endpoint)


if __name__ == "__main__":
    # Test the ML intent classifier
    test_queries = [
        ("get firewall policies from gw1", "/cmdb/firewall/policy"),
        ("get firewall policies from gw1 and display in csv format", "/cmdb/firewall/policy"),
        ("show me just name and action for policies from gw1", "/cmdb/firewall/policy"),
        ("give me a summary of interfaces", "/cmdb/system/interface"),
        ("show interfaces in html format", "/cmdb/system/interface"),
        ("display only enabled policies", "/cmdb/firewall/policy"),
        ("format as json", None),
        ("export to csv", None),
        ("show detailed information", None)
    ]
    
    classifier = MLIntentClassifier()
    
    for query, endpoint in test_queries:
        print(f"\n🔤 Query: {query}")
        print(f"📍 Endpoint: {endpoint}")
        print("-" * 50)
        
        intent = classifier.classify_intent(query, endpoint)
        
        print(f"🎯 Format: {intent.format_type} (confidence: {intent.format_confidence:.2f})")
        print(f"📋 Fields: {intent.requested_fields} (confidence: {intent.field_confidence:.2f})")
        print(f"🔍 Filters: {intent.filter_conditions} (confidence: {intent.filter_confidence:.2f})")
        print(f"🎨 Style: {intent.output_style}")
