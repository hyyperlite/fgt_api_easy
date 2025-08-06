#!/usr/bin/env python3
"""
Intelligent Display Engine

Optimizes the display of FortiGate API response data based on context classification
and user queries. Provides intelligent field selection, data organization, and formatting.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from collections import defaultdict, Counter
import re

import pandas as pd
import numpy as np


class IntelligentDisplayEngine:
    """
    Optimizes data display based on context and user preferences
    """
    
    def __init__(self, context_classifier=None):
        """
        Initialize the display engine
        
        Args:
            context_classifier: EndpointContextClassifier instance
        """
        self.classifier = context_classifier
        self.logger = logging.getLogger(__name__)
        
        # Display templates for different contexts
        self.display_templates = {
            'firewall_policy': {
                'priority_fields': ['policyid', 'name', 'srcaddr', 'dstaddr', 'service', 'action', 'status'],
                'display_format': 'table',
                'max_fields': 8,
                'sort_by': 'policyid',
                'group_by': None,
                'summary_fields': ['action', 'status']
            },
            'firewall_objects': {
                'priority_fields': ['name', 'type', 'subnet', 'member', 'comment'],
                'display_format': 'table',
                'max_fields': 6,
                'sort_by': 'name',
                'group_by': 'type',
                'summary_fields': ['type']
            },
            'routing': {
                'priority_fields': ['dst', 'gateway', 'interface', 'device', 'distance'],
                'display_format': 'table',
                'max_fields': 6,
                'sort_by': 'distance',
                'group_by': 'interface',
                'summary_fields': ['interface']
            },
            'vpn': {
                'priority_fields': ['name', 'interface', 'peer', 'status', 'proposal'],
                'display_format': 'table',
                'max_fields': 7,
                'sort_by': 'name',
                'group_by': 'status',
                'summary_fields': ['status']
            },
            'system': {
                'priority_fields': ['name', 'ip', 'status', 'type', 'version'],
                'display_format': 'table',
                'max_fields': 8,
                'sort_by': 'name',
                'group_by': None,
                'summary_fields': ['status', 'type']
            },
            'user_auth': {
                'priority_fields': ['name', 'status', 'type', 'member'],
                'display_format': 'table',
                'max_fields': 6,
                'sort_by': 'name',
                'group_by': 'type',
                'summary_fields': ['status', 'type']
            },
            'monitor': {
                'priority_fields': ['name', 'status', 'rx_bytes', 'tx_bytes', 'rx_packets', 'tx_packets'],
                'display_format': 'table',
                'max_fields': 8,
                'sort_by': 'name',
                'group_by': 'status',
                'summary_fields': ['status']
            },
            'default': {
                'priority_fields': [],
                'display_format': 'table',
                'max_fields': 6,
                'sort_by': None,
                'group_by': None,
                'summary_fields': []
            }
        }
    
    def optimize_display(self, endpoint: str, data: Any, user_query: Optional[str] = None,
                        display_format: Optional[str] = None) -> Dict[str, Any]:
        """
        Optimize data display based on context and user preferences
        
        Args:
            endpoint: API endpoint path
            data: Response data from the endpoint
            user_query: Optional natural language query for filtering/formatting
            display_format: Override display format ('table', 'json', 'summary', 'tree')
            
        Returns:
            Dict containing optimized display configuration and data
        """
        try:
            # Classify the data context if classifier is available
            if self.classifier:
                classification = self.classifier.classify_endpoint_data(endpoint, data)
                context = classification['category']
                confidence = classification['confidence']
            else:
                context = self._simple_context_detection(endpoint)
                confidence = 0.5
            
            # Get appropriate display template
            template = self.display_templates.get(context, self.display_templates['default'])
            
            # Override template with user preferences
            if display_format:
                template = template.copy()
                template['display_format'] = display_format
            
            # Process the data based on template and user query
            processed_data = self._process_data(data, template, user_query)
            
            return {
                'context': context,
                'confidence': confidence,
                'endpoint': endpoint,
                'display_config': template,
                'original_count': self._count_items(data),
                'processed_count': self._count_items(processed_data['data']),
                'processed_data': processed_data,
                'applied_filters': processed_data.get('applied_filters', []),
                'suggestions': self._generate_suggestions(data, template, context)
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing display for {endpoint}: {e}")
            return {
                'context': 'unknown',
                'confidence': 0.0,
                'endpoint': endpoint,
                'display_config': self.display_templates['default'],
                'error': str(e),
                'processed_data': {'data': data, 'fields': [], 'format': 'raw'}
            }
    
    def _process_data(self, data: Any, template: Dict[str, Any], 
                     user_query: Optional[str] = None) -> Dict[str, Any]:
        """
        Process data according to template and user query
        
        Args:
            data: Raw data to process
            template: Display template configuration
            user_query: Optional user query for additional processing
            
        Returns:
            Dict containing processed data and metadata
        """
        if not data:
            return {'data': data, 'fields': [], 'format': template['display_format']}
        
        processed_data = data
        applied_filters = []
        
        # Convert to list format if needed
        if isinstance(data, dict):
            data_list = [data]
        elif isinstance(data, list):
            data_list = data
        else:
            return {'data': data, 'fields': [], 'format': 'raw'}
        
        # Apply user query filters if provided
        if user_query:
            filtered_data, filters = self._apply_user_query(data_list, user_query)
            data_list = filtered_data
            applied_filters.extend(filters)
        
        # Select optimal fields
        selected_fields = self._select_optimal_fields(data_list, template)
        
        # Sort data if specified
        if template.get('sort_by') and data_list:
            try:
                reverse_sort = 'desc' in user_query.lower() if user_query else False
                data_list = self._sort_data(data_list, template['sort_by'], reverse=reverse_sort)
            except Exception as e:
                self.logger.warning(f"Could not sort by {template['sort_by']}: {e}")
        
        # Group data if specified
        grouped_data = None
        if template.get('group_by') and len(data_list) > 1:
            try:
                grouped_data = self._group_data(data_list, template['group_by'])
            except Exception as e:
                self.logger.warning(f"Could not group by {template['group_by']}: {e}")
        
        return {
            'data': data_list,
            'fields': selected_fields,
            'format': template['display_format'],
            'grouped_data': grouped_data,
            'applied_filters': applied_filters,
            'sort_by': template.get('sort_by'),
            'group_by': template.get('group_by')
        }
    
    def _select_optimal_fields(self, data_list: List[Dict[str, Any]], 
                              template: Dict[str, Any]) -> List[str]:
        """
        Select the most relevant fields for display
        
        Args:
            data_list: List of data objects
            template: Display template
            
        Returns:
            List of selected field names
        """
        if not data_list:
            return []
        
        # Get all available fields
        all_fields = set()
        for item in data_list[:10]:  # Sample first 10 items
            if isinstance(item, dict):
                all_fields.update(item.keys())
        
        # Start with priority fields from template
        selected_fields = []
        priority_fields = template.get('priority_fields', [])
        
        for field in priority_fields:
            if field in all_fields:
                selected_fields.append(field)
        
        # Add additional important fields
        max_fields = template.get('max_fields', 6)
        if len(selected_fields) < max_fields:
            # Score remaining fields by importance
            field_scores = self._score_fields(data_list, set(selected_fields))
            
            # Add highest scoring fields
            remaining_slots = max_fields - len(selected_fields)
            top_fields = sorted(field_scores.items(), key=lambda x: x[1], reverse=True)
            
            for field, score in top_fields[:remaining_slots]:
                if field not in selected_fields:
                    selected_fields.append(field)
        
        return selected_fields
    
    def _score_fields(self, data_list: List[Dict[str, Any]], 
                     exclude_fields: set) -> Dict[str, float]:
        """
        Score fields by their importance and information content
        
        Args:
            data_list: List of data objects
            exclude_fields: Fields to exclude from scoring
            
        Returns:
            Dict mapping field names to importance scores
        """
        field_scores = defaultdict(float)
        
        for item in data_list[:20]:  # Sample for scoring
            if not isinstance(item, dict):
                continue
                
            for field, value in item.items():
                if field in exclude_fields:
                    continue
                
                score = 0.0
                
                # Score based on field name importance
                field_lower = field.lower()
                if any(keyword in field_lower for keyword in ['name', 'id', 'status']):
                    score += 2.0
                elif any(keyword in field_lower for keyword in ['type', 'version', 'address']):
                    score += 1.5
                elif any(keyword in field_lower for keyword in ['comment', 'description']):
                    score += 0.5
                
                # Score based on value content
                if value is not None and str(value).strip():
                    score += 1.0
                    
                    # Prefer shorter, more readable values
                    str_value = str(value)
                    if len(str_value) < 50:
                        score += 0.5
                    if len(str_value) < 20:
                        score += 0.3
                
                field_scores[field] += score
        
        # Normalize scores
        if field_scores:
            max_score = max(field_scores.values())
            for field in field_scores:
                field_scores[field] /= max_score
        
        return dict(field_scores)
    
    def _apply_user_query(self, data_list: List[Dict[str, Any]], 
                         user_query: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Apply user query filters to data
        
        Args:
            data_list: List of data objects
            user_query: User's natural language query
            
        Returns:
            Tuple of (filtered_data, applied_filters)
        """
        filtered_data = data_list.copy()
        applied_filters = []
        
        query_lower = user_query.lower()
        
        # Simple keyword filtering
        if 'only' in query_lower or 'filter' in query_lower or 'show' in query_lower:
            # Extract filter keywords
            keywords = self._extract_filter_keywords(user_query)
            if keywords:
                original_count = len(filtered_data)
                filtered_data = self._filter_by_keywords(filtered_data, keywords)
                applied_filters.append(f"Filtered by keywords: {', '.join(keywords)}")
                if len(filtered_data) != original_count:
                    applied_filters.append(f"Reduced from {original_count} to {len(filtered_data)} items")
        
        # Status filtering
        if any(status in query_lower for status in ['enabled', 'disabled', 'active', 'inactive']):
            status_filter = None
            if 'enabled' in query_lower or 'active' in query_lower:
                status_filter = lambda x: str(x.get('status', '')).lower() in ['enabled', 'active', 'up']
            elif 'disabled' in query_lower or 'inactive' in query_lower:
                status_filter = lambda x: str(x.get('status', '')).lower() in ['disabled', 'inactive', 'down']
            
            if status_filter:
                original_count = len(filtered_data)
                filtered_data = [item for item in filtered_data if status_filter(item)]
                applied_filters.append(f"Filtered by status, reduced from {original_count} to {len(filtered_data)} items")
        
        return filtered_data, applied_filters
    
    def _extract_filter_keywords(self, query: str) -> List[str]:
        """Extract filter keywords from user query"""
        # Simple keyword extraction - can be enhanced
        query = query.lower()
        
        # Remove common words
        stop_words = {'show', 'only', 'filter', 'by', 'with', 'the', 'a', 'an', 'and', 'or'}
        words = [word.strip('.,!?;:') for word in query.split()]
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:5]  # Limit to 5 keywords
    
    def _filter_by_keywords(self, data_list: List[Dict[str, Any]], 
                           keywords: List[str]) -> List[Dict[str, Any]]:
        """Filter data by keywords"""
        filtered_data = []
        
        for item in data_list:
            # Check if any keyword appears in the item's values
            item_text = ' '.join(str(v).lower() for v in item.values() if v is not None)
            
            if any(keyword.lower() in item_text for keyword in keywords):
                filtered_data.append(item)
        
        return filtered_data
    
    def _sort_data(self, data_list: List[Dict[str, Any]], sort_field: str, 
                   reverse: bool = False) -> List[Dict[str, Any]]:
        """Sort data by specified field"""
        def sort_key(item):
            value = item.get(sort_field, '')
            # Handle different data types
            if isinstance(value, (int, float)):
                return value
            elif isinstance(value, str):
                # Try to convert to number if possible
                try:
                    return float(value)
                except ValueError:
                    return value.lower()
            else:
                return str(value).lower()
        
        return sorted(data_list, key=sort_key, reverse=reverse)
    
    def _group_data(self, data_list: List[Dict[str, Any]], 
                    group_field: str) -> Dict[str, List[Dict[str, Any]]]:
        """Group data by specified field"""
        grouped = defaultdict(list)
        
        for item in data_list:
            group_value = str(item.get(group_field, 'Unknown'))
            grouped[group_value].append(item)
        
        return dict(grouped)
    
    def _simple_context_detection(self, endpoint: str) -> str:
        """Simple rule-based context detection when classifier is not available"""
        endpoint_lower = endpoint.lower()
        
        if 'policy' in endpoint_lower:
            return 'firewall_policy'
        elif any(term in endpoint_lower for term in ['address', 'service']):
            return 'firewall_objects'
        elif 'route' in endpoint_lower:
            return 'routing'
        elif 'vpn' in endpoint_lower:
            return 'vpn'
        elif 'user' in endpoint_lower:
            return 'user_auth'
        elif 'monitor' in endpoint_lower:
            return 'monitor'
        elif 'system' in endpoint_lower:
            return 'system'
        else:
            return 'default'
    
    def _count_items(self, data: Any) -> int:
        """Count items in data structure"""
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            return 1
        else:
            return 0
    
    def _generate_suggestions(self, data: Any, template: Dict[str, Any], 
                            context: str) -> List[str]:
        """Generate helpful suggestions for the user"""
        suggestions = []
        
        if not data:
            return suggestions
        
        # Count-based suggestions
        item_count = self._count_items(data)
        if item_count > 50:
            suggestions.append("Consider using filters to narrow down results (e.g., 'show only enabled')")
        
        # Context-specific suggestions
        if context == 'firewall_policy':
            suggestions.append("Try: 'show only enabled policies' or 'filter by source address'")
        elif context == 'routing':
            suggestions.append("Try: 'sort by distance' or 'group by interface'")
        elif context == 'vpn':
            suggestions.append("Try: 'show only active tunnels' or 'filter by status'")
        
        # Format suggestions
        if template['display_format'] == 'table' and item_count > 20:
            suggestions.append("Consider 'summary' format for large datasets")
        
        return suggestions
    
    def create_custom_template(self, category: str, priority_fields: List[str], 
                             display_format: str = 'table', **kwargs) -> Dict[str, Any]:
        """Create a custom display template"""
        template = {
            'priority_fields': priority_fields,
            'display_format': display_format,
            'max_fields': kwargs.get('max_fields', 6),
            'sort_by': kwargs.get('sort_by'),
            'group_by': kwargs.get('group_by'),
            'summary_fields': kwargs.get('summary_fields', [])
        }
        
        self.display_templates[category] = template
        return template


if __name__ == "__main__":
    # Quick test
    engine = IntelligentDisplayEngine()
    
    test_data = [
        {"policyid": 1, "name": "Allow_Web", "srcaddr": "internal", "dstaddr": "all", "action": "accept", "status": "enabled"},
        {"policyid": 2, "name": "Block_Social", "srcaddr": "internal", "dstaddr": "social_media", "action": "deny", "status": "enabled"}
    ]
    
    result = engine.optimize_display("/cmdb/firewall/policy", test_data, "show only enabled")
    print(f"Display optimization result: {json.dumps(result, indent=2)}")
