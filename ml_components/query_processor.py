#!/usr/bin/env python3
"""
Query Processor

Processes natural language queries for FortiGate API data filtering,
sorting, and display customization using local NLP models.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from collections import defaultdict
import json

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    import warnings
    warnings.warn("sentence-transformers not available, using fallback query processing")


class QueryProcessor:
    """
    Processes natural language queries to extract intent and parameters
    for data filtering and display customization.
    """
    
    def __init__(self, use_embeddings: bool = True):
        """
        Initialize the query processor
        
        Args:
            use_embeddings: Whether to use sentence embeddings (requires sentence-transformers)
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize sentence transformer if available and requested
        self.model = None
        if use_embeddings and SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # Use a small, efficient model that works offline
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.logger.info("Loaded sentence transformer model for query processing")
            except Exception as e:
                self.logger.warning(f"Could not load sentence transformer: {e}")
        
        # Define query intents and their patterns
        self.query_intents = {
            'filter': {
                'patterns': [
                    r'\b(show|display|list)\s+(only|just)\s+(.+)',
                    r'\b(filter|limit)\s+by\s+(.+)',
                    r'\b(exclude|remove|hide)\s+(.+)',
                    r'\b(where|with)\s+(.+)',
                    r'\b(find|search)\s+(.+)'
                ],
                'keywords': ['show', 'filter', 'only', 'exclude', 'where', 'find', 'search', 'with']
            },
            'sort': {
                'patterns': [
                    r'\b(sort|order|arrange)\s+by\s+(.+)',
                    r'\b(order)\s+(.+)\s+(ascending|descending|asc|desc)',
                    r'\b(arrange)\s+(.+)'
                ],
                'keywords': ['sort', 'order', 'arrange', 'ascending', 'descending', 'asc', 'desc']
            },
            'group': {
                'patterns': [
                    r'\b(group|organize)\s+by\s+(.+)',
                    r'\b(categorize)\s+by\s+(.+)',
                    r'\b(group)\s+(.+)'
                ],
                'keywords': ['group', 'organize', 'categorize']
            },
            'summarize': {
                'patterns': [
                    r'\b(summarize|summary|overview|count)\s*(.+)?',
                    r'\b(total|sum|aggregate)\s+(.+)',
                    r'\bhow\s+many\b(.+)?'
                ],
                'keywords': ['summary', 'summarize', 'overview', 'total', 'count', 'how many']
            },
            'format': {
                'patterns': [
                    r'\b(format|display|show)\s+as\s+(table|json|tree|list)',
                    r'\b(table|json|tree|list)\s+format',
                    r'\bin\s+(table|json|tree|list)\s+format'
                ],
                'keywords': ['format', 'table', 'json', 'tree', 'list']
            },
            'limit': {
                'patterns': [
                    r'\b(limit|top|first|last)\s+(\d+)',
                    r'\bshow\s+(\d+)\s+(items|results|entries)',
                    r'\b(\d+)\s+(items|results|entries)'
                ],
                'keywords': ['limit', 'top', 'first', 'last']
            }
        }
        
        # Common field mappings and synonyms
        self.field_synonyms = {
            'name': ['name', 'names', 'named'],
            'status': ['status', 'state', 'enabled', 'disabled', 'active', 'inactive'],
            'address': ['address', 'addr', 'ip', 'subnet'],
            'policy': ['policy', 'policies', 'rule', 'rules'],
            'interface': ['interface', 'intf', 'port'],
            'service': ['service', 'services', 'port', 'ports'],
            'source': ['source', 'src', 'from'],
            'destination': ['destination', 'dst', 'dest', 'to'],
            'action': ['action', 'allow', 'deny', 'accept', 'block'],
            'type': ['type', 'kind', 'category']
        }
        
        # Value mappings for common terms
        self.value_mappings = {
            'enabled': ['enabled', 'active', 'on', 'up', 'true', 'yes'],
            'disabled': ['disabled', 'inactive', 'off', 'down', 'false', 'no'],
            'allow': ['allow', 'permit', 'accept', 'enable'],
            'deny': ['deny', 'block', 'drop', 'reject', 'disable']
        }
    
    def process_query(self, user_query: str, data_structure: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a natural language query to extract intent and parameters
        
        Args:
            user_query: The user's natural language query
            data_structure: Optional sample of the data structure for context
            
        Returns:
            Dict containing processed query information
        """
        try:
            query_lower = user_query.lower().strip()
            
            # Extract primary intent
            intent, confidence = self._classify_intent(query_lower)
            
            # Extract parameters based on intent
            parameters = self._extract_parameters(query_lower, intent, data_structure)
            
            # Extract additional modifiers
            modifiers = self._extract_modifiers(query_lower)
            
            # Generate execution plan
            execution_plan = self._create_execution_plan(intent, parameters, modifiers)
            
            return {
                'original_query': user_query,
                'primary_intent': intent,
                'confidence': confidence,
                'parameters': parameters,
                'modifiers': modifiers,
                'execution_plan': execution_plan,
                'suggestions': self._generate_query_suggestions(query_lower, intent)
            }
            
        except Exception as e:
            self.logger.error(f"Error processing query '{user_query}': {e}")
            return {
                'original_query': user_query,
                'primary_intent': 'unknown',
                'confidence': 0.0,
                'parameters': {},
                'error': str(e)
            }
    
    def _classify_intent(self, query: str) -> Tuple[str, float]:
        """
        Classify the primary intent of the query
        
        Args:
            query: Lowercased query string
            
        Returns:
            Tuple of (intent, confidence_score)
        """
        intent_scores = defaultdict(float)
        
        # Pattern-based classification
        for intent, config in self.query_intents.items():
            # Check regex patterns
            for pattern in config['patterns']:
                if re.search(pattern, query, re.IGNORECASE):
                    intent_scores[intent] += 2.0
            
            # Check keywords
            for keyword in config['keywords']:
                if keyword in query:
                    intent_scores[intent] += 1.0
        
        # Use embeddings if available
        if self.model and SENTENCE_TRANSFORMERS_AVAILABLE:
            embedding_scores = self._classify_with_embeddings(query)
            for intent, score in embedding_scores.items():
                intent_scores[intent] += score
        
        # Determine best intent
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            max_score = intent_scores[best_intent]
            confidence = min(1.0, max_score / 5.0)  # Normalize to 0-1
            return best_intent, confidence
        
        return 'filter', 0.2  # Default to filter with low confidence
    
    def _classify_with_embeddings(self, query: str) -> Dict[str, float]:
        """
        Classify intent using sentence embeddings
        
        Args:
            query: Query string
            
        Returns:
            Dict mapping intent to similarity score
        """
        if not self.model:
            return {}
        
        try:
            # Define example queries for each intent
            intent_examples = {
                'filter': ["show only enabled policies", "filter by source address", "find active rules"],
                'sort': ["sort by name", "order by policy ID", "arrange by priority"],
                'group': ["group by interface", "organize by type", "categorize by status"],
                'summarize': ["show summary", "count total policies", "how many rules"],
                'format': ["display as table", "show in json format", "format as tree"],
                'limit': ["show top 10", "limit to 5 items", "first 20 results"]
            }
            
            # Get embedding for user query
            query_embedding = self.model.encode([query])
            
            scores = {}
            for intent, examples in intent_examples.items():
                # Get embeddings for examples
                example_embeddings = self.model.encode(examples)
                
                # Calculate similarity
                similarities = np.dot(query_embedding, example_embeddings.T).flatten()
                scores[intent] = float(np.max(similarities))
            
            return scores
            
        except Exception as e:
            self.logger.warning(f"Error in embedding-based classification: {e}")
            return {}
    
    def _extract_parameters(self, query: str, intent: str, 
                          data_structure: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract parameters specific to the identified intent
        
        Args:
            query: Lowercased query string
            intent: Identified intent
            data_structure: Optional data structure for context
            
        Returns:
            Dict containing extracted parameters
        """
        parameters = {}
        
        if intent == 'filter':
            parameters.update(self._extract_filter_parameters(query, data_structure))
        elif intent == 'sort':
            parameters.update(self._extract_sort_parameters(query, data_structure))
        elif intent == 'group':
            parameters.update(self._extract_group_parameters(query, data_structure))
        elif intent == 'summarize':
            parameters.update(self._extract_summary_parameters(query, data_structure))
        elif intent == 'format':
            parameters.update(self._extract_format_parameters(query))
        elif intent == 'limit':
            parameters.update(self._extract_limit_parameters(query))
        
        return parameters
    
    def _extract_filter_parameters(self, query: str, 
                                 data_structure: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract filter parameters from query"""
        params = {'filters': []}
        
        # Extract field-value pairs
        patterns = [
            r'\b(only|just)\s+([a-zA-Z_]+)\s*=?\s*([^\s,]+)',
            r'\bwhere\s+([a-zA-Z_]+)\s*(is|=|equals?)\s*([^\s,]+)',
            r'\b([a-zA-Z_]+)\s+(is|equals?|contains?)\s+([^\s,]+)',
            r'\bwith\s+([a-zA-Z_]+)\s+([^\s,]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                if len(match) >= 2:
                    field = self._normalize_field_name(match[-2])
                    value = self._normalize_value(match[-1])
                    params['filters'].append({'field': field, 'value': value, 'operator': 'equals'})
        
        # Extract status filters
        status_patterns = [
            r'\b(enabled|active|on|up)\b',
            r'\b(disabled|inactive|off|down)\b'
        ]
        
        for pattern in status_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                status_value = 'enabled' if pattern == status_patterns[0] else 'disabled'
                params['filters'].append({'field': 'status', 'value': status_value, 'operator': 'equals'})
        
        # Extract keyword search
        search_match = re.search(r'\b(find|search|containing?)\s+(.+?)(?:\s+in|\s+by|$)', query, re.IGNORECASE)
        if search_match:
            params['search_term'] = search_match.group(2).strip()
        
        return params
    
    def _extract_sort_parameters(self, query: str,
                               data_structure: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract sort parameters from query"""
        params = {}
        
        # Extract sort field
        sort_patterns = [
            r'\b(?:sort|order|arrange)\s+by\s+([a-zA-Z_]+)',
            r'\b([a-zA-Z_]+)\s+(?:ascending|descending|asc|desc)'
        ]
        
        for pattern in sort_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                params['sort_field'] = self._normalize_field_name(match.group(1))
                break
        
        # Extract sort direction
        if re.search(r'\b(descending|desc|reverse)\b', query, re.IGNORECASE):
            params['sort_direction'] = 'desc'
        else:
            params['sort_direction'] = 'asc'
        
        return params
    
    def _extract_group_parameters(self, query: str,
                                data_structure: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract grouping parameters from query"""
        params = {}
        
        # Extract group field
        group_patterns = [
            r'\b(?:group|organize|categorize)\s+by\s+([a-zA-Z_]+)',
            r'\bby\s+([a-zA-Z_]+)\s+(?:group|category)'
        ]
        
        for pattern in group_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                params['group_field'] = self._normalize_field_name(match.group(1))
                break
        
        return params
    
    def _extract_summary_parameters(self, query: str,
                                  data_structure: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract summary parameters from query"""
        params = {'summary_type': 'count'}
        
        if re.search(r'\b(total|sum)\b', query, re.IGNORECASE):
            params['summary_type'] = 'sum'
        elif re.search(r'\b(average|mean)\b', query, re.IGNORECASE):
            params['summary_type'] = 'average'
        elif re.search(r'\b(count|how many)\b', query, re.IGNORECASE):
            params['summary_type'] = 'count'
        
        # Extract field to summarize
        summary_field_match = re.search(r'\b(?:total|count|sum)\s+(?:of\s+)?([a-zA-Z_]+)', query, re.IGNORECASE)
        if summary_field_match:
            params['summary_field'] = self._normalize_field_name(summary_field_match.group(1))
        
        return params
    
    def _extract_format_parameters(self, query: str) -> Dict[str, Any]:
        """Extract format parameters from query"""
        params = {}
        
        formats = ['table', 'json', 'tree', 'list', 'summary']
        for fmt in formats:
            if fmt in query:
                params['format'] = fmt
                break
        
        return params
    
    def _extract_limit_parameters(self, query: str) -> Dict[str, Any]:
        """Extract limit parameters from query"""
        params = {}
        
        # Extract limit number
        limit_patterns = [
            r'\b(?:limit|top|first|last)\s+(\d+)',
            r'\bshow\s+(\d+)',
            r'\b(\d+)\s+(?:items|results|entries)'
        ]
        
        for pattern in limit_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                params['limit'] = int(match.group(1))
                break
        
        # Determine if it's from start or end
        if re.search(r'\b(?:last|bottom)\b', query, re.IGNORECASE):
            params['from_end'] = True
        else:
            params['from_end'] = False
        
        return params
    
    def _extract_modifiers(self, query: str) -> Dict[str, Any]:
        """Extract additional modifiers from query"""
        modifiers = {}
        
        # Case sensitivity
        if re.search(r'\bcase[- ]sensitive\b', query, re.IGNORECASE):
            modifiers['case_sensitive'] = True
        
        # Exact match
        if re.search(r'\bexact\b', query, re.IGNORECASE):
            modifiers['exact_match'] = True
        
        # Include/exclude nulls
        if re.search(r'\binclude\s+(?:null|empty)\b', query, re.IGNORECASE):
            modifiers['include_nulls'] = True
        elif re.search(r'\bexclude\s+(?:null|empty)\b', query, re.IGNORECASE):
            modifiers['include_nulls'] = False
        
        return modifiers
    
    def _normalize_field_name(self, field: str) -> str:
        """Normalize field name using synonyms"""
        field_lower = field.lower().strip()
        
        for canonical_field, synonyms in self.field_synonyms.items():
            if field_lower in synonyms:
                return canonical_field
        
        return field_lower
    
    def _normalize_value(self, value: str) -> str:
        """Normalize field value using mappings"""
        value_lower = value.lower().strip()
        
        for canonical_value, synonyms in self.value_mappings.items():
            if value_lower in synonyms:
                return canonical_value
        
        return value.strip()
    
    def _create_execution_plan(self, intent: str, parameters: Dict[str, Any], 
                             modifiers: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create an execution plan from the processed query"""
        plan = []
        
        if intent == 'filter':
            if 'filters' in parameters and parameters['filters']:
                plan.append({'action': 'filter', 'params': parameters['filters']})
            if 'search_term' in parameters:
                plan.append({'action': 'search', 'params': {'term': parameters['search_term']}})
        
        elif intent == 'sort':
            if 'sort_field' in parameters:
                plan.append({
                    'action': 'sort', 
                    'params': {
                        'field': parameters['sort_field'],
                        'direction': parameters.get('sort_direction', 'asc')
                    }
                })
        
        elif intent == 'group':
            if 'group_field' in parameters:
                plan.append({'action': 'group', 'params': {'field': parameters['group_field']}})
        
        elif intent == 'summarize':
            plan.append({
                'action': 'summarize',
                'params': {
                    'type': parameters.get('summary_type', 'count'),
                    'field': parameters.get('summary_field')
                }
            })
        
        elif intent == 'format':
            if 'format' in parameters:
                plan.append({'action': 'format', 'params': {'format': parameters['format']}})
        
        elif intent == 'limit':
            if 'limit' in parameters:
                plan.append({
                    'action': 'limit',
                    'params': {
                        'count': parameters['limit'],
                        'from_end': parameters.get('from_end', False)
                    }
                })
        
        return plan
    
    def _generate_query_suggestions(self, query: str, intent: str) -> List[str]:
        """Generate suggestions for improving the query"""
        suggestions = []
        
        if intent == 'unknown' or intent == 'filter':
            suggestions.extend([
                "Try: 'show only enabled items'",
                "Try: 'filter by status = active'",
                "Try: 'find items containing keyword'"
            ])
        
        if intent in ['filter', 'sort']:
            suggestions.append("You can combine operations: 'show enabled policies sorted by name'")
        
        if len(query.split()) < 3:
            suggestions.append("Try being more specific about what you want to see")
        
        return suggestions[:3]  # Limit suggestions


if __name__ == "__main__":
    # Quick test
    processor = QueryProcessor()
    
    test_queries = [
        "show only enabled policies",
        "sort by name descending",
        "group by interface",
        "summarize count by status",
        "display as json format",
        "limit to top 10 results"
    ]
    
    for query in test_queries:
        result = processor.process_query(query)
        print(f"Query: '{query}'")
        print(f"Intent: {result['primary_intent']} (confidence: {result['confidence']:.2f})")
        print(f"Parameters: {result['parameters']}")
        print(f"Plan: {result['execution_plan']}")
        print("---")
