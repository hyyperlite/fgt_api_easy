#!/usr/bin/env python3
"""
FortiGate API Schema Builder

This script connects to a FortiGate device to discover and document its REST API.
It probes a list of potential endpoints to infer their schema, supported methods,
and other metadata. The output is a structured JSON file that serves as a
knowledge base for the AI/ML components of the fgt_api_client.

This script is intended to be run once to generate the initial schema, which can
then be manually curated and enriched with descriptions and key field information.
"""

import argparse
import json
import sys
from typing import Dict, Any, List, Optional

# Add parent directory to path to import client
sys.path.append('.')
from fgt_api_client import FortiGateAPIClient, load_config_file

# --- Configuration ---
# A comprehensive list of potential endpoints to probe.
# This list should be expanded over time to cover more of the FortiGate API.
# We group them by likely categories to help with initial classification.
ENDPOINTS_TO_PROBE = {
    "firewall_policy": [
        "/cmdb/firewall/policy",
        "/cmdb/firewall/policy6",
        "/cmdb/firewall/policy46",
        "/cmdb/firewall/policy64",
    ],
    "firewall_objects": [
        "/cmdb/firewall/address",
        "/cmdb/firewall/addrgrp",
        "/cmdb/firewall/service/custom",
        "/cmdb/firewall/service/group",
        "/cmdb/firewall/schedule/onetime",
        "/cmdb/firewall/schedule/recurring",
    ],
    "routing": [
        "/cmdb/router/static",
        "/cmdb/router/static6",
        "/cmdb/router/bgp",
        "/cmdb/router/ospf",
        "/monitor/router/ipv4",
        "/monitor/router/ipv6",
    ],
    "system": [
        "/cmdb/system/interface",
        "/cmdb/system/dns",
        "/cmdb/system/global",
        "/cmdb/system/admin",
        "/monitor/system/status",
        "/monitor/system/performance",
    ],
    "vpn": [
        "/cmdb/vpn.ssl/settings",
        "/cmdb/vpn.ipsec/phase1-interface",
        "/cmdb/vpn.ipsec/phase2-interface",
        "/monitor/vpn/ipsec",
        "/monitor/vpn/ssl",
    ],
    "user_auth": [
        "/cmdb/user/local",
        "/cmdb/user/group",
        "/cmdb/user/ldap",
    ],
    "security_profiles": [
        "/cmdb/antivirus/profile",
        "/cmdb/webfilter/profile",
        "/cmdb/application/list",
        "/cmdb/ips/sensor",
    ],
    "logging": [
        "/log/memory/filter",
        "/log/disk/filter",
        "/log/fortianalyzer/filter",
    ]
}

OUTPUT_FILE = "api_schema.json"

class APISchemaBuilder:
    """
    Probes a FortiGate API to build a schema of its endpoints.
    """
    def __init__(self, client: FortiGateAPIClient):
        self.client = client
        self.api_schema = {}

    def build_schema(self):
        """
        Iterates through the endpoint list and builds the schema for each one.
        """
        print("Starting API schema discovery...")
        for category, endpoints in ENDPOINTS_TO_PROBE.items():
            print(f"\n--- Probing Category: {category} ---")
            for endpoint in endpoints:
                print(f"  -> Probing endpoint: {endpoint}...")
                schema_entry = self._probe_endpoint(endpoint, category)
                if schema_entry:
                    self.api_schema[endpoint] = schema_entry
                    print(f"  ✅ Success: Schema generated for {endpoint}")
                else:
                    print(f"  ❌ Failed: Could not generate schema for {endpoint}")
        
        self._save_schema()

    def _probe_endpoint(self, endpoint: str, category: str) -> Optional[Dict[str, Any]]:
        """
        Probes a single endpoint to determine its schema and supported methods.
        """
        # 1. Perform a GET request to get sample data and infer schema
        status_code, response = self.client.execute_request('get', endpoint)

        if status_code != 200 or not response:
            # If the endpoint doesn't respond to a simple GET, we can't infer much.
            # It might not exist or might require specific parameters.
            return None

        # 2. Infer the schema from the response
        data_sample = response.get('results', [])
        if not isinstance(data_sample, list) or not data_sample:
            # Handle single-object responses or empty lists
            if isinstance(response.get('results'), dict):
                 data_sample = [response.get('results')]
            else:
                # Cannot infer schema from this response
                return None
        
        inferred_schema = self._infer_schema_from_data(data_sample[0])

        # 3. Determine supported HTTP methods (this is a simplified inference)
        methods = self._infer_methods(endpoint)

        # 4. Assemble the schema entry
        return {
            "description": f"Manages {category.replace('_', ' ')}.",
            "category": category,
            "methods": methods,
            "key_fields": list(inferred_schema.keys())[:5],  # Default to first 5 fields
            "schema": inferred_schema
        }

    def _infer_schema_from_data(self, item: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """
        Infers a basic schema from a single data item (dictionary).
        """
        schema = {}
        for key, value in item.items():
            field_type = "string" # Default
            if isinstance(value, bool):
                field_type = "boolean"
            elif isinstance(value, int):
                field_type = "integer"
            elif isinstance(value, list):
                field_type = "list"
            elif isinstance(value, dict):
                field_type = "object"
            
            schema[key] = {"type": field_type}
        return schema

    def _infer_methods(self, endpoint: str) -> List[str]:
        """
        Infers supported HTTP methods based on the endpoint path.
        This is a simplified approach. A real implementation might use OPTIONS requests.
        """
        if endpoint.startswith('/cmdb/'):
            return ["GET", "POST", "PUT", "DELETE"]
        elif endpoint.startswith('/monitor/'):
            return ["GET"]
        elif endpoint.startswith('/log/'):
            return ["GET"]
        else:
            return ["GET"] # Default assumption

    def _save_schema(self):
        """
        Saves the generated schema to the output file.
        """
        if not self.api_schema:
            print("\nNo schema information was generated. Nothing to save.")
            return

        print(f"\nSaving generated schema to {OUTPUT_FILE}...")
        try:
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(self.api_schema, f, indent=2)
            print("✅ Schema saved successfully.")
            print(f"\nNext steps:")
            print(f"1. Review the generated '{OUTPUT_FILE}'.")
            print(f"2. Manually add meaningful 'description' for each endpoint.")
            print(f"3. Curate the 'key_fields' list for each endpoint to define the most important fields for default display.")

        except IOError as e:
            print(f"Error saving schema file: {e}", file=sys.stderr)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="FortiGate API Schema Builder",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-c', '--config', metavar='FILE', required=True,
                        help='Configuration file path for the FortiGate device (e.g., config.ini)')
    args = parser.parse_args()

    # Load configuration to get connection details
    try:
        config = load_config_file(args.config)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)

    host = config.get('host') or config.get('ip')
    apikey = config.get('apikey')

    if not host or not apikey:
        print("Error: 'host' and 'apikey' must be defined in the configuration file.", file=sys.stderr)
        sys.exit(1)

    # Create the API client
    client = FortiGateAPIClient(
        host=host,
        apikey=apikey,
        use_ssl=config.get('use_ssl', 'true').lower() == 'true',
        verify_ssl=config.get('verify_ssl', 'false').lower() == 'true'
    )

    # Build and save the schema
    builder = APISchemaBuilder(client)
    builder.build_schema()

if __name__ == "__main__":
    main()
