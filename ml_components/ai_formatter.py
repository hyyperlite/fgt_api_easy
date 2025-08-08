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
import datetime
import os
from typing import Dict, List, Any, Optional, Union

# Import the canonical UserIntent dataclass
from .user_intent import UserIntent


class AIDataFormatter:
    """AI-powered data formatter that interprets user intent."""
    
    def format_data(self, data: Union[Dict, List], intent: UserIntent) -> str:
        """
        Formats data based on a pre-parsed UserIntent object.
        """
        items = self._extract_data_from_response(data)
        if not items:
            return "No data to display."

        if intent.filter_conditions and intent.filter_confidence > 0.6:
            items = self._apply_structured_filters(items, intent.filter_conditions)

        sample_record = items[0] if items else {}
        if intent.requested_fields and intent.field_confidence > 0.6:
            selected_fields = self._validate_and_select_fields(sample_record, intent.requested_fields)
        else:
            selected_fields = self._ai_select_intelligent_fields(sample_record, intent.endpoint, intent.format_type)
        
        format_type = intent.format_type.lower()
        if format_type == 'summary':
            return self._format_as_summary(items, selected_fields, intent.endpoint)
        elif format_type == 'csv':
            return self._format_as_csv(items, selected_fields)
        elif format_type == 'tsv':
            return self._format_as_tsv(items, selected_fields)
        elif format_type == 'json':
            return self._format_as_json(items, intent.output_style)
        elif format_type == 'html':
            return self._format_as_html(items, selected_fields)
        elif format_type == 'pdf':
            return self._format_as_pdf(items, selected_fields, intent)
        elif format_type == 'list':
            return self._format_as_list(items, selected_fields, intent.output_style)
        else:  # Default to table
            return self._format_as_table(items, selected_fields)

    def _apply_structured_filters(self, items: List[Dict], filters: List[Dict[str, Any]]) -> List[Dict]:
        """Apply filtering logic based on a structured list of conditions."""
        if not filters or not items:
            return items

        filtered_items = items[:]
        for f in filters:
            field = f.get("field")
            operator = f.get("operator")
            value = f.get("value")

            if not all([field, operator, value is not None]):
                continue

            temp_items = []
            for item in filtered_items:
                item_value = item.get(field)
                if item_value is None:
                    continue

                match = False
                try:
                    if isinstance(item_value, (int, float)):
                        # Numeric comparison
                        if value is None: continue
                        value_to_compare = type(item_value)(value)
                        if operator == "==": match = (item_value == value_to_compare)
                        elif operator == "!=": match = (item_value != value_to_compare)
                        elif operator == ">=": match = (item_value >= value_to_compare)
                        elif operator == "<=": match = (item_value <= value_to_compare)
                        elif operator == ">": match = (item_value > value_to_compare)
                        elif operator == "<": match = (item_value < value_to_compare)
                    elif isinstance(item_value, str):
                        # String comparison
                        item_value_lower = item_value.lower()
                        value_to_compare = str(value).lower()
                        if operator == "==": match = (item_value_lower == value_to_compare)
                        elif operator == "!=": match = (item_value_lower != value_to_compare)
                        elif operator == "contains": match = (value_to_compare in item_value_lower)
                        elif operator == "startswith": match = (item_value_lower.startswith(value_to_compare))
                        elif operator == "endswith": match = (item_value_lower.endswith(value_to_compare))
                except (ValueError, TypeError):
                    # Handles cases where `value` cannot be cast to the item's numeric type
                    continue
                
                if match:
                    temp_items.append(item)
            
            filtered_items = temp_items
        
        return filtered_items

    def _format_as_pdf(self, items: List[Dict], selected_fields: List[str], intent: UserIntent) -> str:
        """Format data as a PDF file."""
        try:
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            from reportlab.lib.units import inch
        except ImportError:
            return "❌ PDF generation requires 'reportlab'. Please install it (`pip install reportlab`)."

        if not items:
            return "No data to generate PDF."

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, rightMargin=inch/2, leftMargin=inch/2, topMargin=inch/2, bottomMargin=inch/2)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph(f"Report for Endpoint: {intent.endpoint}", styles['h1']))

        table_data = [selected_fields]
        for item in items:
            table_data.append([str(item.get(field, '')) for field in selected_fields])

        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"report_{timestamp}.pdf"
        pdf_path = os.path.join("/tmp", pdf_filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(buffer.getvalue())
        
        return f"✅ Successfully generated PDF report: {pdf_path}"

    def _format_as_csv(self, items: List[Dict], selected_fields: List[str]) -> str:
        """Format data as CSV"""
        if not items: return ""
        output = io.StringIO()
        fieldnames = selected_fields or items[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow({f: item.get(f, '') for f in fieldnames})
        return output.getvalue()
    
    def _format_as_tsv(self, items: List[Dict], selected_fields: List[str]) -> str:
        """Format data as TSV"""
        if not items: return ""
        output = io.StringIO()
        fieldnames = selected_fields or list(items[0].keys())
        output.write('\t'.join(fieldnames) + '\n')
        for item in items:
            output.write('\t'.join([str(item.get(f, '')) for f in fieldnames]) + '\n')
        return output.getvalue()
    
    def _format_as_json(self, items: List[Dict], style: str) -> str:
        """Format data as JSON"""
        indent = 2 if style != 'brief' else None
        return json.dumps(items, indent=indent, default=str)
    
    def _format_as_html(self, items: List[Dict], selected_fields: List[str]) -> str:
        """Format data as HTML table"""
        if not items: return "<p>No data available</p>"
        headers = selected_fields or list(items[0].keys())
        html = ["<table border='1' style='border-collapse: collapse;'>", "<tr>"]
        for header in headers:
            html.append(f"<th style='padding: 8px; background-color: #f2f2f2;'>{header}</th>")
        html.append("</tr>")
        for item in items:
            html.append("<tr>")
            for header in headers:
                html.append(f"<td style='padding: 8px;'>{item.get(header, '')}</td>")
            html.append("</tr>")
        html.append("</table>")
        return "\n".join(html)
    
    def _format_as_list(self, items: List[Dict], selected_fields: List[str], style: str) -> str:
        """Format data as a bullet list"""
        if not items: return "• No items to display"
        lines = []
        fields_to_show = selected_fields or (list(items[0].keys()) if items else [])
        for i, item in enumerate(items, 1):
            if style == 'brief' and fields_to_show:
                lines.append(f"• {item.get(fields_to_show[0], 'N/A')}")
            else:
                lines.append(f"• Item {i}:")
                for key in fields_to_show:
                    lines.append(f"  - {key}: {item.get(key, 'N/A')}")
        return "\n".join(lines)
    
    def _format_as_table(self, items: List[Dict], selected_fields: List[str]) -> str:
        """Format data as an ASCII table"""
        if not items: return "No data to display in table format."
        try:
            from tabulate import tabulate
        except ImportError:
            return "Table format requires 'tabulate'. Please install it (`pip install tabulate`)."
        
        headers = selected_fields or list(items[0].keys())
        table_data = [{h: item.get(h, '') for h in headers} for item in items]
        return tabulate(table_data, headers="keys", tablefmt="grid")
    
    def _extract_data_from_response(self, raw_data: Union[Dict[str, Any], List]) -> List[Dict[str, Any]]:
        """Extract data list from various possible response formats."""
        if isinstance(raw_data, list):
            return raw_data
        if isinstance(raw_data, dict):
            if 'results' in raw_data and isinstance(raw_data['results'], list):
                return raw_data['results']
            if 'data' in raw_data and isinstance(raw_data['data'], list):
                return raw_data['data']
            for value in raw_data.values():
                if isinstance(value, list) and all(isinstance(i, dict) for i in value):
                    return value
            return [raw_data]
        return []
    
    def _ai_select_intelligent_fields(self, sample_record: Dict[str, Any], endpoint: str, format_type: str) -> List[str]:
        """AI-driven intelligent field selection."""
        if not sample_record: return []
        all_fields = list(sample_record.keys())
        
        priority_map = {
            '/firewall/policy': ['policyid', 'name', 'srcintf', 'dstintf', 'srcaddr', 'dstaddr', 'action', 'status'],
            '/system/interface': ['name', 'ip', 'status', 'type', 'vdom', 'description'],
            '/vpn/ipsec': ['name', 'remote-gw', 'status', 'interface', 'proposal']
        }
        
        for key, fields in priority_map.items():
            if key in endpoint:
                priority_fields = fields
                break
        else:
            priority_fields = [f for f in ['name', 'id', 'status', 'type'] if f in all_fields]

        selected = [f for f in priority_fields if f in all_fields]
        
        max_fields = 10 if format_type in ['table', 'csv', 'html', 'pdf'] else 5
        for field in all_fields:
            if len(selected) >= max_fields: break
            if field not in selected:
                selected.append(field)
        
        return selected

    def _validate_and_select_fields(self, sample_record: Dict[str, Any], requested_fields: List[str]) -> List[str]:
        """Validate that requested fields exist in the data."""
        if not sample_record: return []
        available_fields = list(sample_record.keys())
        valid_fields = []
        for r_field in requested_fields:
            if r_field in available_fields:
                if r_field not in valid_fields: valid_fields.append(r_field)
            else:
                for a_field in available_fields:
                    if r_field.lower() in a_field.lower():
                        if a_field not in valid_fields: valid_fields.append(a_field)
                        break
        return valid_fields or available_fields[:5]
    
    def _format_as_summary(self, data_list: List[Dict[str, Any]], fields: List[str], endpoint: str) -> str:
        """Create an AI-generated summary."""
        total_count = len(data_list)
        summary_lines = [f"📊 **Summary for {endpoint}**", f"   Total Records: {total_count}", ""]
        if not data_list: return "\n".join(summary_lines)

        if '/firewall/policy' in endpoint:
            status_counts = {}
            for item in data_list:
                status = "enable" if str(item.get('status', '')).lower() == 'enable' else "disable"
                status_counts[status] = status_counts.get(status, 0) + 1
            summary_lines.append("   **Policy Status:**")
            for status, count in status_counts.items():
                summary_lines.append(f"      • {status.capitalize()}: {count}")
        
        if data_list:
            summary_lines.extend(["", "   **Sample Records (Top 5):**", ""])
            summary_lines.append(self._format_as_table(data_list[:5], fields))
        
        return "\n".join(summary_lines)

def format_with_ai(data: Union[List[Dict], Dict], intent: UserIntent) -> str:
    """Main function to format data using AI-powered natural language processing."""
    formatter = AIDataFormatter()
    return formatter.format_data(data, intent)

if __name__ == "__main__":
    # This block is for testing the formatter directly.
    from .enhanced_intent_classifier import classify_user_intent

    sample_data = {
        "results": [
            {"policyid": 1, "name": "Allow_Web", "srcaddr": "internal", "dstaddr": "all", "action": "accept", "status": "enable"},
            {"policyid": 2, "name": "Block_Social", "srcaddr": "users", "dstaddr": "social_media", "action": "deny", "status": "enable"},
            {"policyid": 3, "name": "VPN_Access", "srcaddr": "vpn_users", "dstaddr": "servers", "action": "accept", "status": "disable"}
        ]
    }
    
    test_queries = [
        "show me just the name and action fields",
        "give me a summary of this data",
        "format as CSV",
        "show only enabled policies where action is accept"
    ]
    
    endpoint = "/cmdb/firewall/policy"
    formatter = AIDataFormatter()

    for query in test_queries:
        print(f"\n🔤 Query: '{query}'")
        print("=" * 60)
        intent = classify_user_intent(query, endpoint)
        if intent:
            result = formatter.format_data(sample_data, intent)
            print(result)
        else:
            print("Could not classify intent.")
        print()
