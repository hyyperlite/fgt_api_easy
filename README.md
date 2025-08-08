# FortiGate API Client with AI/ML

An intelligent Python command-line application for interacting with FortiGate devices, enhanced with built-in AI/ML capabilities for natural language queries and smart data formatting.

## ✨ Features

### Core Functionality
- **Full REST API Support**: Execute GET, POST, PUT, and DELETE requests.
- **Flexible Authentication**: Use an API key or traditional username/password.
- **Centralized Configuration**: Manage host credentials and settings from `config/` directory files (INI or JSON).
- **Standard Output Formatting**: View results as a standard table or as raw/pretty JSON.

### 🤖 AI/ML Capabilities
- **Natural Language Queries**: Interact with the API using plain English commands.
- **Interactive Shell**: A powerful, conversational interface for exploring your FortiGate configuration.
- **Intelligent Data Formatting**: Automatically formats output into tables, lists, CSV, JSON, and can generate PDF reports based on your request.
- **Smart Filtering & Field Selection**: Filter results and select specific fields to display using natural language (e.g., "show enabled policies with just the name and action fields").
- **100% Local Processing**: All AI/ML models run locally. No data is ever sent to external services.

## 🚀 Quick Start

### 1. Installation
The `install.sh` script handles everything from setting up the Python environment to installing dependencies.
```bash
git clone https://github.com/hyyperlite/fgt_api_easy.git
cd fgt_api_generic
./install.sh
```

### 2. Configuration
Host configurations are loaded from the `config/` directory. You can define your FortiGate devices in either `config/hosts.json` or by creating new `.ini` files.
```bash
# Copy the example host configuration
cp config.json.example config/hosts.json

# Then, edit config/hosts.json to add your devices
# {
#   "hosts": {
#     "my-firewall": {
#       "ip": "192.168.1.99",
#       "apikey": "your-api-key-here"
#     }
#   }
# }
```

## 📖 Usage

The best way to experience the AI-powered features is through the interactive shell.

### Interactive Mode
Start the interactive shell by running the client with the `--interactive` flag.
```bash
python3 fgt_api_client.py --interactive
```
Once inside the shell, you can issue natural language commands. The AI will parse your request, connect to the correct host, fetch the data, and format it according to your instructions.

**Example Session:**
```
fgt> show firewall policies as a table from my-firewall
✅ Success! Fetched and formatted data from my-firewall.
<... table output of firewall policies ...>

fgt> list enabled policies from my-firewall, just the name and status
✅ Success! Fetched and formatted data from my-firewall.
- Policy1: enabled
- Policy2: enabled

fgt> generate a pdf report of the routing table from my-firewall
✅ Success! PDF report generated at: /tmp/report_20250808_123456.pdf
```

### Command-Line Mode
You can also execute standard, non-AI queries directly from the command line.
```bash
# Standard GET request
python3 fgt_api_client.py -i 192.168.1.99 -k <api_key> -m get -e /cmdb/firewall/address

# Create a new object
python3 fgt_api_client.py -i 192.168.1.99 -k <api_key> -m post -e /cmdb/firewall/address -d '{"name": "new_host", "subnet": "10.0.0.1/32"}'
```
For AI-powered queries outside the interactive shell, use the `--ai-query` argument.
```bash
python3 fgt_api_client.py --ai-query "show enabled policies as a csv from my-firewall"
```

## 🧪 Testing
A comprehensive test suite is available to validate the AI pipeline.
```bash
python3 -m unittest test_ai_features.py
```

## 📁 Project Structure
The application is organized into the main client and a dedicated `ml_components` package.
```
fgt_api_generic/
├── fgt_api_client.py       # Main application script
├── ml_components/          # All AI/ML related modules
│   ├── __init__.py
│   ├── user_intent.py      # Defines the structure of a user's request
│   ├── enhanced_intent_classifier.py # Parses natural language into a UserIntent
│   ├── ai_formatter.py     # Formats data based on the UserIntent
│   ├── model_trainer.py    # Script to train the classification models
│   └── models/             # Directory for trained ML models
├── test_ai_features.py     # Test suite for the AI pipeline
├── requirements.txt        # Python package dependencies
└── README.md               # This file
```
