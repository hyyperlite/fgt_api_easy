#!/usr/bin/env python3
"""
AI-Powered Dynamic Formatter

This component uses AI/LLM capabilities to intelligently format data
based on natural language requests from users.
"""

import json
import re
import csv
import io
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class FormattingRequest:
    """Represents a user's formatting request parsed from natural language"""
    
    def __init__(self, format_type: str = 'table', fields: List[str] = None, 
                 filters: Dict[str, Any] = None, sort_by: Optional[str] = None,
                 limit: Optional[int] = None, style: str = 'standard',
                 user_query: str = '', endpoint: str = ''):
        self.format_type = format_type
        self.fields = fields or []
        self.filters = filters or {}
        self.sort_by = sort_by
        self.limit = limit
        self.style = style
        self.user_query = user_query
        self.endpoint = endpoint


class AIDataFormatter:
    """AI-powered data formatter that interprets natural language requests"""
    
    def __init__(self):
        self.format_patterns = {
            'table': r'\b(table|tabular|columns?|rows?)\b',
            'csv': r'\b(csv|comma.separated)\b',
            'tsv': r'\b(tsv|tab.separated)\b', 
            'json': r'\b(json|javascript)\b',
            'html': r'\b(html|web|webpage)\b',
            'pdf': r'\b(pdf|document)\b',
            'summary': r'\b(summar[yi]|overview|brief|digest)\b',
            'list': r'\b(list|bullet|enumerate)\b',
            'raw': r'\b(raw|plain|unformatted)\b'
        }
        
        self.field_extraction_patterns = [
            r'\bonly\s+([\w\s,]+?)(?:\s+from|\s+where|\s*$)',
            r'\bshow\s+(?:me\s+)?(?:only\s+)?([\w\s,]+?)(?:\s+from|\s+where|\s*$)',
            r'\bjust\s+([\w\s,]+?)(?:\s+from|\s+where|\s*$)',
            r'\bfields?\s+([\w\s,]+?)(?:\s+from|\s+where|\s*$)',
            r'\bcolumns?\s+([\w\s,]+?)(?:\s+from|\s+where|\s*$)'
        ]
        
        self.filter_patterns = [
            r'\bwhere\s+(.*?)(?:\s+(?:order|sort|limit)|\s*$)',
            r'\bfilter(?:ed)?\s+(?:by\s+)?(.*?)(?:\s+(?:order|sort|limit)|\s*$)',
            r'\bcontain(?:ing|s)\s+(.*?)(?:\s+(?:order|sort|limit)|\s*$)',
            r'\bmatch(?:ing)?\s+(.*?)(?:\s+(?:order|sort|limit)|\s*$)'
        ]
    
    def parse_formatting_request(self, user_query: str, available_fields: List[str] = None) -> FormattingRequest:
        """Parse user's natural language request into formatting instructions"""
        query_lower = user_query.lower()
        
        # Detect format type
        format_type = 'auto'
        for fmt, pattern in self.format_patterns.items():
            if re.search(pattern, query_lower, re.IGNORECASE):
                format_type = fmt
                break
        
        # If no specific format detected, infer from context
        if format_type == 'auto':
            if any(word in query_lower for word in ['brief', 'overview', 'what', 'summary']):
                format_type = 'summary'
            elif any(word in query_lower for word in ['list', 'show me', 'display']):
                format_type = 'table'
            else:
                format_type = 'table'  # default
        
        # Extract specific fields requested
        requested_fields = []
        for pattern in self.field_extraction_patterns:
            match = re.search(pattern, user_query, re.IGNORECASE)
            if match:
                fields_text = match.group(1)
                # Parse comma-separated fields
                fields = [f.strip() for f in re.split(r'[,\s]+(?:and\s+)?', fields_text) if f.strip()]
                requested_fields.extend(fields)
                break
        
        # Extract filters
        filters = {}
        for pattern in self.filter_patterns:
            match = re.search(pattern, user_query, re.IGNORECASE)
            if match:
                filter_text = match.group(1).strip()
                # Simple filter parsing (can be enhanced)
                filters['condition'] = filter_text
                break
        
        # Extract sorting
        sort_by = None
        sort_match = re.search(r'\b(?:sort|order)\s+by\s+(\w+)', query_lower)
        if sort_match:
            sort_by = sort_match.group(1)
        
        # Extract limit
        limit = None
        limit_match = re.search(r'\b(?:limit|top|first)\s+(\d+)', query_lower)
        if limit_match:
            limit = int(limit_match.group(1))
        elif 'brief' in query_lower or 'summary' in query_lower:
            limit = 10  # Default for summaries
        
        # Detect style
        style = 'standard'
        if any(word in query_lower for word in ['brief', 'short', 'compact']):
            style = 'brief'
        elif any(word in query_lower for word in ['detailed', 'verbose', 'full']):
            style = 'detailed'
        elif any(word in query_lower for word in ['minimal', 'basic']):
            style = 'minimal'
        
        return FormattingRequest(
            format_type=format_type,
            fields=requested_fields,
            filters=filters,
            sort_by=sort_by,
            limit=limit,
            style=style,
            user_query=user_query
        )
    
    def apply_ai_formatting(self, data: Union[List[Dict], Dict], 
                           formatting_request: FormattingRequest,
                           endpoint: str = None) -> str:
        """Apply AI-powered formatting based on user request"""
        
        # Normalize data to list format
        if isinstance(data, dict):
            if 'results' in data:
                items = data['results']
            elif any(key in data for key in ['data', 'items', 'entries']):
                key = next(k for k in ['data', 'items', 'entries'] if k in data)
                items = data[key]
            else:
                items = [data]
        else:
            items = data if isinstance(data, list) else [data]
        
        if not items:
            return "No data to display."
        
        # Apply filtering
        if formatting_request.filters:
            items = self._apply_filters(items, formatting_request.filters)
        
        # Apply field selection
        if formatting_request.fields:
            items = self._select_fields(items, formatting_request.fields)
        
        # Apply sorting
        if formatting_request.sort_by:
            items = self._sort_data(items, formatting_request.sort_by)
        
        # Apply limit
        if formatting_request.limit:
            items = items[:formatting_request.limit]
        
        # Format based on requested type
        if formatting_request.format_type == 'summary':
            return self._format_as_summary(items, formatting_request)
        elif formatting_request.format_type == 'csv':
            return self._format_as_csv(items)
        elif formatting_request.format_type == 'tsv':
            return self._format_as_tsv(items)
        elif formatting_request.format_type == 'json':
            return self._format_as_json(items, formatting_request.style)
        elif formatting_request.format_type == 'html':
            return self._format_as_html(items, formatting_request)
        elif formatting_request.format_type == 'list':
            return self._format_as_list(items, formatting_request)
        elif formatting_request.format_type == 'raw':
            return self._format_as_raw(items)
        else:  # table or auto
            return self._format_as_table(items, formatting_request)
    
    def _apply_filters(self, items: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Apply filtering logic to data"""
        if not filters or not items:
            return items
        
        condition = filters.get('condition', '').lower()
        if not condition:
            return items
        
        filtered_items = []
        for item in items:
            # Simple text-based filtering
            item_text = json.dumps(item, default=str).lower()
            if condition in item_text:
                filtered_items.append(item)
            else:
                # Check individual fields
                for key, value in item.items():
                    if condition in str(value).lower():
                        filtered_items.append(item)
                        break
        
        return filtered_items
    
    def _select_fields(self, items: List[Dict], requested_fields: List[str]) -> List[Dict]:
        """Select only specific fields from data"""
        if not requested_fields or not items:
            return items
        
        # Find actual field names that match requested fields (fuzzy matching)
        if items:
            available_fields = list(items[0].keys())
            matched_fields = []
            
            for requested in requested_fields:
                requested_lower = requested.lower().replace(' ', '_')
                # Exact match first
                for field in available_fields:
                    if field.lower() == requested_lower:
                        matched_fields.append(field)
                        break
                else:
                    # Partial match
                    for field in available_fields:
                        if requested_lower in field.lower() or field.lower() in requested_lower:
                            matched_fields.append(field)
                            break
            
            if matched_fields:
                return [{field: item.get(field, 'N/A') for field in matched_fields} for item in items]
        
        return items
    
    def _sort_data(self, items: List[Dict], sort_field: str) -> List[Dict]:
        """Sort data by specified field"""
        if not items:
            return items
        
        # Find matching field name
        available_fields = list(items[0].keys())
        actual_field = None
        
        for field in available_fields:
            if field.lower() == sort_field.lower():
                actual_field = field
                break
        
        if actual_field:
            try:
                return sorted(items, key=lambda x: x.get(actual_field, ''))
            except:
                pass  # Ignore sorting errors
        
        return items
    
    def _format_as_csv(self, items: List[Dict], selected_fields: List[str] = None) -> str:
        """Format data as CSV"""
        if not items:
            return ""
        
        output = io.StringIO()
        if items and isinstance(items[0], dict):
            # Use selected fields if provided, otherwise all fields
            if selected_fields:
                fieldnames = [f for f in selected_fields if f in items[0]]
            else:
                fieldnames = items[0].keys()
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write only the selected fields for each item
            for item in items:
                if selected_fields:
                    filtered_item = {f: item.get(f, '') for f in fieldnames}
                    writer.writerow(filtered_item)
                else:
                    writer.writerow(item)
        
        return output.getvalue()
    
    def _format_as_tsv(self, items: List[Dict]) -> str:
        """Format data as TSV"""
        if not items:
            return ""
        
        output = io.StringIO()
        if items and isinstance(items[0], dict):
            fieldnames = list(items[0].keys())
            # Header
            output.write('\t'.join(fieldnames) + '\n')
            # Data
            for item in items:
                values = [str(item.get(field, '')) for field in fieldnames]
                output.write('\t'.join(values) + '\n')
        
        return output.getvalue()
    
    def _format_as_json(self, items: List[Dict], style: str) -> str:
        """Format data as JSON"""
        if style == 'brief':
            return json.dumps(items, indent=2, default=str)[:1000] + "..." if len(str(items)) > 1000 else json.dumps(items, indent=2, default=str)
        else:
            return json.dumps(items, indent=2, default=str)
    
    def _format_as_html(self, items: List[Dict], formatting_request: FormattingRequest) -> str:
        """Format data as HTML table"""
        if not items:
            return "<p>No data available</p>"
        
        html = ["<table border='1' style='border-collapse: collapse;'>"]
        
        if isinstance(items[0], dict):
            # Header
            headers = list(items[0].keys())
            html.append("<tr>")
            for header in headers:
                html.append(f"<th style='padding: 8px; background-color: #f2f2f2;'>{header}</th>")
            html.append("</tr>")
            
            # Data rows
            for item in items:
                html.append("<tr>")
                for header in headers:
                    value = item.get(header, '')
                    html.append(f"<td style='padding: 8px;'>{value}</td>")
                html.append("</tr>")
        
        html.append("</table>")
        return "\n".join(html)
    
    def _format_as_list(self, items: List[Dict], formatting_request: FormattingRequest) -> str:
        """Format data as a bullet list"""
        if not items:
            return "• No items to display"
        
        lines = []
        for i, item in enumerate(items, 1):
            if isinstance(item, dict):
                if formatting_request.style == 'brief':
                    # Show just the first field or a summary
                    first_key = list(item.keys())[0] if item else 'item'
                    first_value = list(item.values())[0] if item else 'N/A'
                    lines.append(f"• {first_key}: {first_value}")
                else:
                    lines.append(f"• Item {i}:")
                    for key, value in item.items():
                        lines.append(f"  - {key}: {value}")
            else:
                lines.append(f"• {item}")
        
        return "\n".join(lines)
    
    def _format_as_table(self, items: List[Dict], formatting_request: FormattingRequest) -> str:
        """Format data as an ASCII table"""
        if not items:
            return "No data to display in table format."
        
        if not isinstance(items[0], dict):
            return str(items)
        
        headers = list(items[0].keys())
        
        # Calculate column widths
        col_widths = {}
        for header in headers:
            col_widths[header] = len(str(header))
            for item in items:
                value_len = len(str(item.get(header, '')))
                col_widths[header] = max(col_widths[header], value_len)
        
        lines = []
        
        # Header
        header_line = "| " + " | ".join(h.ljust(col_widths[h]) for h in headers) + " |"
        separator = "|-" + "-|-".join("-" * col_widths[h] for h in headers) + "-|"
        
        lines.append(header_line)
        lines.append(separator)
        
        # Data rows
        for item in items:
            row = "| " + " | ".join(str(item.get(h, '')).ljust(col_widths[h]) for h in headers) + " |"
            lines.append(row)
        
        return "\n".join(lines)
    
    def _format_as_raw(self, items: List[Dict]) -> str:
        """Format data as raw text"""
        return str(items)
    
    def format_with_complete_ai(self, raw_data: Dict[str, Any], user_request: str, endpoint: str) -> str:
        """
        Complete AI processing: receives raw JSON and user request, outputs formatted result
        
        This is the main method that should be used for AI-powered formatting.
        It handles everything from understanding the user's intent to producing final output.
        
        Args:
            raw_data: Raw JSON response from FortiGate API
            user_request: User's original natural language request  
            endpoint: API endpoint that was called
            
        Returns:
            Formatted string output ready for display
        """
        
        try:
            # Step 1: Use enhanced ML to understand user intent
            from .enhanced_intent_classifier import get_enhanced_intent_classifier
            classifier = get_enhanced_intent_classifier()
            intent = classifier.classify_intent(user_request, endpoint)
            
            print(f"   🧠 AI Intent Analysis:")
            print(f"      Format: {intent.format_type} (confidence: {intent.format_confidence:.2f})")
            print(f"      Fields: {intent.requested_fields if intent.requested_fields else 'auto-select'}")
            print(f"      Filters: {intent.filter_conditions if intent.filter_conditions else 'none'}")
            
            # Step 2: Extract data from raw response
            data_list = self._extract_data_from_response(raw_data)
            if not data_list:
                return "❌ No data found in API response"
            
            print(f"   📊 Data extracted: {len(data_list)} records")
            
            # Step 3: Apply AI-driven field selection
            if intent.requested_fields and intent.field_confidence > 0.6:
                # User requested specific fields
                selected_fields = self._validate_and_select_fields(data_list[0], intent.requested_fields)
                print(f"   🎯 User-requested fields: {selected_fields}")
            else:
                # AI auto-select intelligent fields based on endpoint
                selected_fields = self._ai_select_intelligent_fields(data_list[0], endpoint, intent.format_type)
                print(f"   🤖 AI-selected fields: {selected_fields}")
            
            # Step 4: Apply filters if requested
            if intent.filter_conditions and intent.filter_confidence > 0.7:
                filtered_data = self._apply_ai_filters(data_list, intent.filter_conditions)
                print(f"   🔍 Applied filters: {len(filtered_data)} records remaining")
            else:
                filtered_data = data_list
            
            # Step 5: Format according to detected intent
            if intent.format_type == 'csv':
                output = self._format_as_csv(filtered_data, selected_fields)
            elif intent.format_type == 'json':
                # For JSON, we don't need field selection since it's structured data
                output = self._format_as_json(filtered_data, "formatted")
            elif intent.format_type == 'html':
                # Create a FormattingRequest for HTML
                formatting_req = FormattingRequest(
                    fields=selected_fields,
                    format_type='html',
                    endpoint=endpoint
                )
                output = self._format_as_html(filtered_data, formatting_req)
            elif intent.format_type == 'table':
                # Create a FormattingRequest for table
                formatting_req = FormattingRequest(
                    fields=selected_fields,
                    format_type='table',
                    endpoint=endpoint
                )
                output = self._format_as_table(filtered_data, formatting_req)
            elif intent.format_type == 'summary':
                # Call the advanced summary method
                output = self._format_as_summary(filtered_data, selected_fields, endpoint)
            else:
                # Default to intelligent table format
                formatting_req = FormattingRequest(
                    fields=selected_fields,
                    format_type='table',
                    endpoint=endpoint
                )
                output = self._format_as_table(filtered_data, formatting_req)
            
            return output
            
        except Exception as e:
            return f"❌ AI formatting error: {e}"
    
    def _extract_data_from_response(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract data list from various possible response formats"""
        
        # FortiGate API typically returns data in 'results' field
        if 'results' in raw_data:
            data = raw_data['results']
        elif 'data' in raw_data:
            data = raw_data['data']
        else:
            # Try to use the raw data directly if it's a list
            data = raw_data
        
        # Ensure we have a list
        if isinstance(data, dict):
            return [data]
        elif isinstance(data, list):
            return data
        else:
            return []
    
    def _ai_select_intelligent_fields(self, sample_record: Dict[str, Any], endpoint: str, format_type: str) -> List[str]:
        """AI-driven intelligent field selection based on endpoint and format"""
        
        all_fields = list(sample_record.keys())
        
        # Endpoint-specific intelligence
        if '/firewall/policy' in endpoint:
            # For firewall policies, prioritize the most important fields
            priority_fields = ['name', 'policyid', 'srcaddr', 'dstaddr', 'service', 'action', 'status']
            secondary_fields = ['srcintf', 'dstintf', 'schedule', 'comments']
        elif '/system/interface' in endpoint:
            priority_fields = ['name', 'status', 'ip', 'type', 'mode']
            secondary_fields = ['vdom', 'mtu', 'speed', 'description']
        elif '/vpn/ipsec' in endpoint:
            priority_fields = ['name', 'remote-gw', 'status', 'interface']
            secondary_fields = ['mode', 'proposal', 'authmethod']
        else:
            # Generic selection
            priority_fields = ['name', 'id', 'status', 'type']
            secondary_fields = []
        
        # Select fields that exist in the data
        selected = []
        
        # Add priority fields first
        for field in priority_fields:
            if field in all_fields:
                selected.append(field)
        
        # Add secondary fields if we have room (based on format)
        max_fields = 12 if format_type in ['table', 'csv'] else 6
        for field in secondary_fields:
            if field in all_fields and len(selected) < max_fields:
                selected.append(field)
        
        # If we still don't have enough fields, add any others
        if len(selected) < 3:
            for field in all_fields:
                if field not in selected and len(selected) < max_fields:
                    selected.append(field)
        
        return selected[:max_fields]
    
    def _validate_and_select_fields(self, sample_record: Dict[str, Any], requested_fields: List[str]) -> List[str]:
        """Validate that requested fields exist in the data"""
        
        available_fields = list(sample_record.keys())
        valid_fields = []
        
        for field in requested_fields:
            # Exact match
            if field in available_fields:
                valid_fields.append(field)
            else:
                # Fuzzy match
                for available in available_fields:
                    if field.lower() in available.lower() or available.lower() in field.lower():
                        valid_fields.append(available)
                        break
        
        return valid_fields if valid_fields else available_fields[:5]
    
    def _apply_ai_filters(self, data_list: List[Dict[str, Any]], filter_conditions: List[str]) -> List[Dict[str, Any]]:
        """Apply intelligent filtering based on natural language conditions"""
        
        filtered_data = data_list
        
        for condition in filter_conditions:
            condition_lower = condition.lower()
            
            # Status-based filters
            if 'enabled' in condition_lower or 'enable' in condition_lower:
                filtered_data = [item for item in filtered_data 
                               if item.get('status', '').lower() in ['enable', 'enabled', 'up', 'active']]
            elif 'disabled' in condition_lower or 'disable' in condition_lower:
                filtered_data = [item for item in filtered_data 
                               if item.get('status', '').lower() in ['disable', 'disabled', 'down', 'inactive']]
            elif 'status is up' in condition_lower:
                filtered_data = [item for item in filtered_data 
                               if item.get('status', '').lower() in ['up', 'enable', 'enabled']]
            
            # Action-based filters (for firewall policies)
            elif 'allow' in condition_lower or 'accept' in condition_lower:
                filtered_data = [item for item in filtered_data 
                               if item.get('action', '').lower() in ['allow', 'accept']]
            elif 'deny' in condition_lower or 'block' in condition_lower:
                filtered_data = [item for item in filtered_data 
                               if item.get('action', '').lower() in ['deny', 'block', 'reject']]
        
        return filtered_data
    
    def _format_as_summary(self, data_list: List[Dict[str, Any]], fields: List[str], endpoint: str) -> str:
        """Create an AI-generated summary"""
        
        total_count = len(data_list)
        
        summary_lines = [
            f"📊 **Summary Report**",
            f"   Total Records: {total_count}",
            ""
        ]
        
        if '/firewall/policy' in endpoint:
            # Firewall policy summary
            enabled_count = len([item for item in data_list if item.get('status', '').lower() == 'enable'])
            disabled_count = total_count - enabled_count
            
            allow_count = len([item for item in data_list if item.get('action', '').lower() == 'allow'])
            deny_count = len([item for item in data_list if item.get('action', '').lower() == 'deny'])
            
            summary_lines.extend([
                f"   📋 **Policy Status:**",
                f"      • Enabled: {enabled_count}",
                f"      • Disabled: {disabled_count}",
                f"   🎯 **Policy Actions:**", 
                f"      • Allow: {allow_count}",
                f"      • Deny: {deny_count}",
                ""
            ])
        
        elif '/system/interface' in endpoint:
            # Interface summary  
            up_count = len([item for item in data_list if item.get('status', '').lower() == 'up'])
            down_count = total_count - up_count
            
            summary_lines.extend([
                f"   🔌 **Interface Status:**",
                f"      • Up: {up_count}",
                f"      • Down: {down_count}",
                ""
            ])
        
        # Add top 5 records in table format
        if data_list:
            summary_lines.extend([
                f"   📋 **Sample Records:**",
                ""
            ])
            
            sample_data = data_list[:5]
            # Create FormattingRequest for table in summary
            table_req = FormattingRequest(
                fields=fields[:4],  # Limit fields for summary
                format_type='table'
            )
            table_output = self._format_as_table(sample_data, table_req)
            summary_lines.append(table_output)
        
        return "\n".join(summary_lines)

def format_with_ai(data: Union[List[Dict], Dict], user_query: str, endpoint: str = None) -> str:
    """Main function to format data using AI-powered natural language processing"""
    formatter = AIDataFormatter()
    formatting_request = formatter.parse_formatting_request(user_query)
    return formatter.apply_ai_formatting(data, formatting_request, endpoint)

if __name__ == "__main__":
    # Test the AI formatter
    sample_data = [
        {"name": "policy1", "action": "allow", "source": "192.168.1.0/24", "destination": "any", "service": "HTTP"},
        {"name": "policy2", "action": "deny", "source": "10.0.0.0/8", "destination": "192.168.1.100", "service": "SSH"},
        {"name": "policy3", "action": "allow", "source": "any", "destination": "192.168.1.50", "service": "HTTPS"}
    ]
    
    test_queries = [
        "show me just the name and action fields",
        "give me a summary of this data",
        "format as CSV",
        "show as a simple list",
        "create an HTML table",
        "show only policies where action is allow"
    ]
    
    for query in test_queries:
        print(f"\n🔤 Query: {query}")
        print("=" * 50)
        result = format_with_ai(sample_data, query)
        print(result)
        print()
