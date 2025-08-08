#!/usr/bin/env python3
"""
Robust Training Data Generator for Enhanced ML Intent Classifier

This script generates a comprehensive and robust training dataset for the
EnhancedMLIntentClassifier. The goal is to create a diverse set of examples
that cover a wide range of user commands, including complex filtering,
various output formats, and combined intents.
"""

import json
import random
import datetime
import os

# Define the structure of the training data
training_data = {
    "description": "Robust, auto-generated training data for FortiGate API client AI",
    "version": "2.0",
    "generated_at": "",
    "examples": []
}

# --- Configuration for Data Generation ---

# Endpoints and their typical fields
ENDPOINTS = {
    "/cmdb/firewall/policy": {
        "fields": ["policyid", "name", "srcintf", "dstintf", "srcaddr", "dstaddr", "action", "status", "comments", "logtraffic"],
        "actions": ["accept", "deny", "ipsec"],
        "statuses": ["enable", "disable"]
    },
    "/cmdb/system/interface": {
        "fields": ["name", "ip", "status", "type", "vdom", "mtu", "speed", "description"],
        "statuses": ["up", "down"],
        "types": ["physical", "vlan", "aggregate"]
    },
    "/cmdb/vpn/ipsec/phase1-interface": {
        "fields": ["name", "remote-gw", "status", "interface", "proposal", "authmethod", "keylife"],
        "statuses": ["up", "down"],
        "auth_methods": ["psk", "signature"]
    },
    "/cmdb/user/local": {
        "fields": ["name", "status", "type", "two-factor", "email"],
        "statuses": ["enable", "disable"],
        "types": ["password", "radius"]
    },
    "/monitor/firewall/session": {
        "fields": ["session_id", "src_ip", "dst_ip", "proto", "duration", "sent_bytes", "rcvd_bytes"],
        "protocols": ["tcp", "udp", "icmp"]
    }
}

# Output formats and their keywords
FORMATS = {
    "table": ["table", "tabular", "columns", "grid"],
    "json": ["json", "raw", "javascript object"],
    "csv": ["csv", "comma separated", "spreadsheet"],
    "html": ["html", "web page", "browser view"],
    "pdf": ["pdf", "document", "report"],
    "summary": ["summary", "overview", "brief", "digest"],
    "list": ["list", "bullet points", "itemized"]
}

# Verbs for requesting data
SHOW_VERBS = ["show", "display", "list", "get", "find", "view", "fetch"]
FIELD_VERBS = ["show only", "just give me", "I only need", "display the"]

# Filter-related keywords
FILTER_KEYWORDS = ["where", "with", "for", "that have", "matching"]
OPERATORS = ["is", "is not", "equals", "contains", "starts with", "ends with"]

# --- Helper Functions ---

def generate_example(intent_type, endpoint_info, endpoint_path):
    """Generates a single training example."""
    example = {
        "query": "",
        "endpoint": endpoint_path,
        "category": endpoint_path.split('/')[2] if len(endpoint_path.split('/')) > 2 else 'unknown',
        "filters": {},
        "fields": [],
        "format": "table" # Default format
    }
    text_parts = [random.choice(SHOW_VERBS)]

    # --- Format Intent ---
    if intent_type in ["format", "combined"]:
        format_type = random.choice(list(FORMATS.keys()))
        example["format"] = format_type
        format_keyword = random.choice(FORMATS[format_type])
        text_parts.append(f"as {format_keyword}")
    else:
        example["format"] = "table"


    # --- Field Intent ---
    if intent_type in ["fields", "combined"]:
        num_fields = random.randint(1, 4)
        requested_fields = random.sample(endpoint_info["fields"], min(num_fields, len(endpoint_info["fields"])))
        example["fields"] = requested_fields
        field_verb = random.choice(FIELD_VERBS)
        text_parts.append(f"{field_verb} {', '.join(requested_fields)}")
    else:
        example["fields"] = []

    # --- Filter Intent ---
    if intent_type in ["filter", "combined"]:
        filter_field = random.choice(endpoint_info["fields"])
        filter_value = f"'{random.choice(['test', 'prod', 'guest', 'default'])}'"
        
        if "statuses" in endpoint_info and "status" in filter_field:
            filter_value = random.choice(endpoint_info["statuses"])
        elif "types" in endpoint_info and "type" in filter_field:
            filter_value = random.choice(endpoint_info["types"])

        filter_keyword = random.choice(FILTER_KEYWORDS)
        operator = random.choice(OPERATORS)
        condition = f"{filter_field} {operator} {filter_value}"
        example["filters"] = {filter_field: f"{operator} {filter_value}"}
        text_parts.append(f"{filter_keyword} {condition}")
    else:
        example["filters"] = {}

    # Combine text parts
    random.shuffle(text_parts)
    # Add a base entity to the query
    entity = endpoint_path.split("/")[-1].replace("-", " ")
    text_parts.append(f"for {entity}")
    
    example["query"] = " ".join(text_parts)


    return example

# --- Main Generation Logic ---

def main():
    """Main function to generate and save the training data."""
    num_examples = 1000
    
    print(f"Generating {num_examples} robust training examples...")

    for _ in range(num_examples):
        intent_type = random.choices(["format", "fields", "filter", "combined"], weights=[0.2, 0.2, 0.3, 0.3])[0]
        endpoint_path, endpoint_info = random.choice(list(ENDPOINTS.items()))
        
        example = generate_example(intent_type, endpoint_info, endpoint_path)
        # Ensure all keys are present
        for key in ['query', 'endpoint', 'category', 'filters', 'fields', 'format']:
            if key not in example:
                if key == 'filters':
                    example[key] = {}
                elif key == 'fields':
                    example[key] = []
                else:
                    example[key] = "" # or some other default
        training_data["examples"].append(example)

    # Add timestamp
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    training_data["generated_at"] = now

    # Save to file
    output_dir = os.path.join(os.path.dirname(__file__), 'training_data')
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"robust_nl_training_data_{now}.json")

    with open(file_path, 'w') as f:
        json.dump(training_data, f, indent=2)

    print(f"\nSuccessfully generated {len(training_data['examples'])} examples.")
    print(f"Training data saved to: {file_path}")
    
    # Print a few examples
    print("\nSample generated examples:")
    for i in range(3):
        print(json.dumps(random.choice(training_data["examples"]), indent=2))

if __name__ == "__main__":
    main()
