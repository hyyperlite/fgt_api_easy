# 🤖 FortiGate API Client - AI/ML Quick Reference

## 🚀 **Essential Commands**

### Check AI Status
```bash
python3 fgt_api_client.py --ai-status
```

### Basic AI-Enhanced Query
```bash
python3 fgt_api_client.py --enable-ai -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/policy
```

### Natural Language Queries
```bash
# Filter data with natural language
python3 fgt_api_client.py --enable-ai --ai-query "show only enabled policies" \
  -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/policy

# Sort results
python3 fgt_api_client.py --enable-ai --ai-query "sort by name descending" \
  -i 192.168.1.99 -k your_api_key -m get -e /cmdb/firewall/address

# Group data
python3 fgt_api_client.py --enable-ai --ai-query "group by interface" \
  -i 192.168.1.99 -k your_api_key -m get -e /cmdb/system/interface
```

## 📊 **Supported AI Queries**

| Intent | Example Query | Description |
|--------|---------------|-------------|
| **Filter** | `"show only enabled policies"` | Filter by status, type, or keyword |
| **Sort** | `"sort by name descending"` | Sort ascending or descending |
| **Group** | `"group by interface"` | Group similar items together |
| **Format** | `"display as json format"` | Change output format |
| **Limit** | `"limit to top 10 results"` | Show only first/last N items |
| **Search** | `"find policies containing web"` | Search for specific terms |

## 🎯 **FortiGate Object Types Supported**

### Firewall Configuration
```bash
# Firewall Policies
python3 fgt_api_client.py --enable-ai --ai-query "show deny policies" \
  -i <host> -k <key> -m get -e /cmdb/firewall/policy

# Address Objects
python3 fgt_api_client.py --enable-ai --ai-format summary \
  -i <host> -k <key> -m get -e /cmdb/firewall/address

# Service Objects
python3 fgt_api_client.py --enable-ai --ai-query "group by protocol" \
  -i <host> -k <key> -m get -e /cmdb/firewall/service/custom
```

### Network Configuration
```bash
# Static Routes
python3 fgt_api_client.py --enable-ai --ai-query "sort by distance" \
  -i <host> -k <key> -m get -e /cmdb/router/static

# Interfaces
python3 fgt_api_client.py --enable-ai --ai-query "show up interfaces" \
  -i <host> -k <key> -m get -e /cmdb/system/interface

# VPN Tunnels
python3 fgt_api_client.py --enable-ai --ai-query "show active VPN tunnels" \
  -i <host> -k <key> -m get -e /monitor/vpn/ipsec
```

### Security & Monitoring
```bash
# Security Profiles
python3 fgt_api_client.py --enable-ai --ai-format table \
  -i <host> -k <key> -m get -e /cmdb/antivirus/profile

# System Status
python3 fgt_api_client.py --enable-ai --ai-format summary \
  -i <host> -k <key> -m get -e /monitor/system/status

# User Authentication
python3 fgt_api_client.py --enable-ai --ai-query "show LDAP users" \
  -i <host> -k <key> -m get -e /cmdb/user/ldap
```

## 🧪 **Testing & Training**

### Local Testing (No FortiGate Required)
```bash
# Run comprehensive demo
python3 ml_demo.py

# Basic component testing
python3 test_ml_basic.py

# Check what's working
python3 fgt_api_client.py --ai-status
```

### Generate Training Data
```bash
# Create enhanced synthetic data
python3 generate_enhanced_training_data.py

# Train models with new data
python3 train_enhanced_models.py

# Collect real data for training
python3 fgt_api_client.py --collect-training-data \
  -i <host> -k <key> -m get -e /cmdb/firewall/policy
```

## 🔧 **AI Format Options**

| Format | Description | Best For |
|--------|-------------|----------|
| `summary` | Key fields only | Quick overview |
| `table` | Structured columns | Multiple items |
| `json` | Full JSON output | Scripting/automation |
| *(default)* | AI-optimized | Context-aware display |

Example:
```bash
python3 fgt_api_client.py --enable-ai --ai-format summary \
  -i <host> -k <key> -m get -e /cmdb/firewall/policy
```

## 📈 **Current Performance**

- **Classification Accuracy**: 94.1%
- **Supported Categories**: 8 (firewall, routing, VPN, system, etc.)
- **Training Examples**: 81 realistic FortiGate configurations
- **Query Processing**: 6 major intent types
- **Privacy**: 100% local processing (no external APIs)

## 🎯 **Real-World Usage Examples**

### Security Audit
```bash
# Find disabled policies
python3 fgt_api_client.py --enable-ai --ai-query "show disabled policies" \
  -i <host> -k <key> -m get -e /cmdb/firewall/policy

# Check for deny rules
python3 fgt_api_client.py --enable-ai --ai-query "show deny policies" \
  -i <host> -k <key> -m get -e /cmdb/firewall/policy

# Review unused addresses
python3 fgt_api_client.py --enable-ai --ai-query "find unused objects" \
  -i <host> -k <key> -m get -e /cmdb/firewall/address
```

### Network Monitoring
```bash
# Interface status
python3 fgt_api_client.py --enable-ai --ai-query "show down interfaces" \
  -i <host> -k <key> -m get -e /monitor/system/interface

# VPN health check
python3 fgt_api_client.py --enable-ai --ai-query "show VPN status" \
  -i <host> -k <key> -m get -e /monitor/vpn/ipsec

# Performance overview
python3 fgt_api_client.py --enable-ai --ai-format summary \
  -i <host> -k <key> -m get -e /monitor/system/performance
```

### Configuration Management
```bash
# Policy review by name
python3 fgt_api_client.py --enable-ai --ai-query "sort policies by name" \
  -i <host> -k <key> -m get -e /cmdb/firewall/policy

# Group addresses by type
python3 fgt_api_client.py --enable-ai --ai-query "group by type" \
  -i <host> -k <key> -m get -e /cmdb/firewall/address

# Route analysis
python3 fgt_api_client.py --enable-ai --ai-query "show routes by distance" \
  -i <host> -k <key> -m get -e /cmdb/router/static
```

---
*For complete documentation, see `ML_AI_IMPLEMENTATION_SUMMARY.md`*
