#!/usr/bin/env python3
"""
Intelligent Formatter for Natural Language Responses

This module provides intelligent formatting that respects user intent for
field selection, data filtering, and output format preferences.
"""

import json
import re
from typing import Any, Dict, List, Optional
from tabulate import tabulate


class IntelligentFormatter:
    """Intelligent formatter that respects natural language user intent"""
    
    def __init__(self):
        self.max_field_width = 50
        self.max_rows_table = 50
        self.max_rows_summary = 10
    
    def format_response(self, data: Any, user_query: str, requested_fields: List[str] = None, 
                       display_format: str = 'table', applied_operations: List[str] = None) -> str:
        """
        Format API response based on user intent
        
        Args:
            data: API response data
            user_query: Original user query for context
            requested_fields: Specific fields user requested
            display_format: Preferred display format (table, json, summary, list)
            applied_operations: List of operations applied to the data
            
        Returns:
            Formatted string output
        """
        try:
            # Add operation summary
            output_parts = []
            
            if applied_operations:
                output_parts.append("🔧 Applied operations:")
                for op in applied_operations:
                    output_parts.append(f"   • {op}")
                output_parts.append("")
            
            # Format based on display preference
            if display_format == 'json':
                formatted_data = self._format_as_json(data)
            elif display_format == 'summary':
                formatted_data = self._format_as_summary(data, user_query)
            elif display_format == 'list':
                formatted_data = self._format_as_list(data, requested_fields)
            else:  # table (default)
                formatted_data = self._format_as_intelligent_table(data, requested_fields, user_query)
            
            output_parts.append(formatted_data)
            
            # Add result count
            count = self._count_items(data)
            if count > 0:
                output_parts.append(f"\n📊 Showing {count} result(s)")
            
            return "\n".join(output_parts)
            
        except Exception as e:
            # Fallback to basic formatting
            return f"❌ Formatting error: {e}\n\n📄 Raw data:\n{json.dumps(data, indent=2, default=str)}"
    
    def _format_as_intelligent_table(self, data: Any, requested_fields: List[str] = None, 
                                   user_query: str = "") -> str:
        """Format data as an intelligent table that respects field requests"""
        try:
            if not isinstance(data, dict) or 'results' not in data:
                return json.dumps(data, indent=2, default=str)
            
            results = data['results']
            if not results:
                return "📝 No results found."
            
            # Get sample item to determine available fields
            sample_item = results[0] if results else {}
            available_fields = list(sample_item.keys()) if isinstance(sample_item, dict) else []
            
            # Determine which fields to display
            if requested_fields:
                # Use only requested fields that exist
                display_fields = []
                for field in requested_fields:
                    # Direct match
                    if field in available_fields:
                        display_fields.append(field)
                    # Partial match
                    else:
                        for available_field in available_fields:
                            if (field.lower() in available_field.lower() or 
                                available_field.lower() in field.lower()):
                                if available_field not in display_fields:
                                    display_fields.append(available_field)
                                break
                
                if not display_fields:
                    return f"❌ Requested fields {requested_fields} not found in data.\n🔍 Available fields: {', '.join(available_fields)}"
            else:
                # Auto-select important fields based on context
                display_fields = self._select_important_fields(available_fields, user_query)
            
            # Build table data
            table_data = []
            headers = display_fields
            
            for item in results[:self.max_rows_table]:
                if isinstance(item, dict):
                    row = []
                    for field in display_fields:
                        value = item.get(field, '')
                        # Truncate long values
                        if isinstance(value, str) and len(value) > self.max_field_width:
                            value = value[:self.max_field_width-3] + "..."
                        row.append(value)
                    table_data.append(row)
            
            if not table_data:
                return "📝 No data to display in table format."
            
            # Format as table
            table_output = tabulate(table_data, headers=headers, tablefmt="grid", 
                                  stralign="left", numalign="left")
            
            # Add truncation notice if needed
            if len(results) > self.max_rows_table:
                table_output += f"\n\n⚠️  Showing first {self.max_rows_table} of {len(results)} results"
            
            return table_output
            
        except Exception as e:
            return f"❌ Table formatting error: {e}\n\n📄 Raw data:\n{json.dumps(data, indent=2, default=str)}"
    
    def _format_as_summary(self, data: Any, user_query: str = "") -> str:
        """Format data as a summary"""
        try:
            if not isinstance(data, dict) or 'results' not in data:
                return f"📊 Summary: Single data item\n{json.dumps(data, indent=2, default=str)}"
            
            results = data['results']
            total_count = len(results)
            
            if total_count == 0:
                return "📊 Summary: No results found"
            
            summary_parts = [f"📊 Summary Report - {total_count} total items"]
            
            # Analyze the data structure
            if results:
                sample_item = results[0]
                if isinstance(sample_item, dict):
                    # Count by status if available
                    status_counts = {}
                    type_counts = {}
                    
                    for item in results:
                        # Count by status
                        status = item.get('status', item.get('enable', 'unknown'))
                        if status:
                            status_counts[status] = status_counts.get(status, 0) + 1
                        
                        # Count by type if available
                        item_type = item.get('type', item.get('category', ''))
                        if item_type:
                            type_counts[item_type] = type_counts.get(item_type, 0) + 1
                    
                    # Add status breakdown
                    if status_counts:
                        summary_parts.append("\n🔍 Status Breakdown:")
                        for status, count in sorted(status_counts.items()):
                            percentage = (count / total_count) * 100
                            summary_parts.append(f"   • {status}: {count} ({percentage:.1f}%)")
                    
                    # Add type breakdown
                    if type_counts and len(type_counts) > 1:
                        summary_parts.append("\n📂 Type Breakdown:")
                        for item_type, count in sorted(type_counts.items()):
                            percentage = (count / total_count) * 100
                            summary_parts.append(f"   • {item_type}: {count} ({percentage:.1f}%)")
                    
                    # Show a few sample items
                    if total_count > 0:
                        summary_parts.append(f"\n📝 Sample items (showing up to {min(self.max_rows_summary, total_count)}):")
                        for i, item in enumerate(results[:self.max_rows_summary]):
                            # Show key identifying fields
                            item_desc = self._describe_item(item)
                            summary_parts.append(f"   {i+1}. {item_desc}")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            return f"❌ Summary formatting error: {e}\n\n📄 Raw data:\n{json.dumps(data, indent=2, default=str)}"
    
    def _format_as_list(self, data: Any, requested_fields: List[str] = None) -> str:
        """Format data as a simple list"""
        try:
            if not isinstance(data, dict) or 'results' not in data:
                return json.dumps(data, indent=2, default=str)
            
            results = data['results']
            if not results:
                return "📝 No results found."
            
            list_parts = []
            
            for i, item in enumerate(results, 1):
                if isinstance(item, dict):
                    if requested_fields:
                        # Show only requested fields
                        item_parts = []
                        for field in requested_fields:
                            if field in item:
                                item_parts.append(f"{field}: {item[field]}")
                        item_desc = " | ".join(item_parts) if item_parts else str(item)
                    else:
                        # Show key identifying information
                        item_desc = self._describe_item(item)
                    
                    list_parts.append(f"{i}. {item_desc}")
                else:
                    list_parts.append(f"{i}. {item}")
            
            return "\n".join(list_parts)
            
        except Exception as e:
            return f"❌ List formatting error: {e}\n\n📄 Raw data:\n{json.dumps(data, indent=2, default=str)}"
    
    def _format_as_json(self, data: Any) -> str:
        """Format data as JSON"""
        try:
            return json.dumps(data, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            return f"❌ JSON formatting error: {e}\n\n📄 Raw data:\n{str(data)}"
    
    def _select_important_fields(self, available_fields: List[str], user_query: str = "") -> List[str]:
        """Select the most important fields to display"""
        # Priority order for common fields
        priority_fields = [
            'policyid', 'id', 'name', 'status', 'enable', 'srcaddr', 'dstaddr', 
            'service', 'action', 'srcintf', 'dstintf', 'comments', 'type'
        ]
        
        selected_fields = []
        
        # Add priority fields that exist
        for field in priority_fields:
            if field in available_fields and field not in selected_fields:
                selected_fields.append(field)
        
        # Add other fields up to a reasonable limit
        for field in available_fields:
            if field not in selected_fields and len(selected_fields) < 6:
                selected_fields.append(field)
        
        return selected_fields[:8]  # Limit to 8 fields for readability
    
    def _describe_item(self, item: Dict[str, Any]) -> str:
        """Create a descriptive string for a data item"""
        # Try to find the most descriptive fields
        desc_parts = []
        
        # Look for ID or name
        for id_field in ['policyid', 'id', 'name']:
            if id_field in item and item[id_field]:
                desc_parts.append(f"{id_field}: {item[id_field]}")
                break
        
        # Look for status
        for status_field in ['status', 'enable', 'state']:
            if status_field in item and item[status_field]:
                desc_parts.append(f"{status_field}: {item[status_field]}")
                break
        
        # Add other key fields
        for key_field in ['srcaddr', 'dstaddr', 'type', 'interface']:
            if key_field in item and item[key_field] and len(desc_parts) < 3:
                desc_parts.append(f"{key_field}: {item[key_field]}")
        
        if desc_parts:
            return " | ".join(desc_parts)
        else:
            # Fallback: show first few non-empty fields
            for key, value in list(item.items())[:3]:
                if value:
                    desc_parts.append(f"{key}: {value}")
            return " | ".join(desc_parts) if desc_parts else str(item)
    
    def _count_items(self, data: Any) -> int:
        """Count items in the data"""
        if isinstance(data, dict) and 'results' in data:
            return len(data['results'])
        elif isinstance(data, list):
            return len(data)
        else:
            return 1 if data else 0
