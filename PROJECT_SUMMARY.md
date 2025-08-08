# FortiGate API Generic Client with AI/ML - Project Summary

## Overview
This project provides a comprehensive Python-based command-line interface for interacting with FortiGate devices. It has been significantly enhanced with a powerful AI/ML pipeline to support natural language queries, intelligent data filtering, and dynamic output formatting. The core goal is to make interacting with the complex FortiGate API as simple as having a conversation.

## Project Structure

The project is organized into core application logic and modular AI/ML components.

```
fgt_api_generic/
├── fgt_api_client.py       # Main application script with command-line parsing
├── fgt                     # Shell wrapper for easier execution
├── ml_components/          # All AI/ML related modules
│   ├── __init__.py
│   ├── user_intent.py      # Canonical UserIntent dataclass (CORE)
│   ├── enhanced_intent_classifier.py # ML-based intent classification
│   ├── ai_formatter.py     # AI-powered data formatter
│   ├── model_trainer.py    # Script to train the classification models
│   ├── generate_training_data.py # Script to create robust training data
│   └── models/             # Directory for trained ML models (.pkl)
├── ml_demo.py              # Script to demonstrate the new AI pipeline
├── test_ai_features.py     # Comprehensive test suite for the AI pipeline
├── requirements.txt        # Python package dependencies
├── README.md               # Comprehensive user documentation
├── PROJECT_PLAN.md         # Detailed project plan and progress tracker
└── ... (other config files and legacy scripts)
```

## Key Features

### Core Functionality
- **Full REST API Support**: GET, POST, PUT, DELETE operations.
- **Flexible Authentication**: API key or username/password.
- **Configuration Management**: Supports INI and JSON config files.

### 🤖 AI/ML Capabilities (New & Enhanced)
- **Natural Language Understanding**: A sophisticated pipeline understands complex user queries involving filtering, field selection, and formatting.
- **Interactive Shell**: The primary interface (`./fgt --interactive`) allows for conversational interaction with the FortiGate API.
- **Intelligent Data Formatting**: Automatically formats data into tables, lists, CSV, JSON, and generates PDF reports based on user intent.
- **Dynamic Filtering**: Applies filters based on natural language (e.g., "show enabled policies").
- **Smart Field Selection**: Intelligently selects relevant fields to display or allows user to specify them (e.g., "show me just the name and status").
- **Local Processing**: All AI/ML processing is done locally; no data is sent to external services.

## Usage

The recommended way to use the application is through the interactive shell.

### Interactive Mode
```bash
./fgt --interactive -c config.ini
```
**Example Session:**
```
fgt> show all firewall policies as a table
... table output ...

fgt> list enabled policies, just the name and status
... list output ...

fgt> generate a pdf report of the routing table
... PDF generated in /tmp ...
```

### Command-Line (for scripting)
```bash
# Use the AI query engine from the command line
./fgt --ai-query "show enabled policies as a csv" -c config.ini -e /cmdb/firewall/policy

# Perform a standard API call without AI
./fgt -c config.ini -m post -e /cmdb/firewall/address -d '{"name": "new_host"}'
```

## AI/ML Pipeline

1.  **Input**: User enters a natural language query (e.g., "list enabled policies as a csv").
2.  **Intent Classification (`enhanced_intent_classifier.py`)**:
    -   Trained ML models (or fallback regex) parse the query to determine the user's intent.
    -   This produces a `UserIntent` object containing the desired format, filters, and fields.
3.  **Data Fetching (`fgt_api_client.py`)**: The client makes the necessary API call to the FortiGate device.
4.  **Intelligent Formatting (`ai_formatter.py`)**:
    -   The formatter takes the raw API data and the `UserIntent` object.
    -   It first applies any requested filters.
    -   Then, it formats the data into the desired output (table, list, CSV, PDF, etc.), selecting the appropriate fields.
5.  **Output**: The final, formatted data is displayed to the user.

## Testing and Validation

The AI/ML pipeline is validated by a comprehensive test suite.

-   **`test_ai_features.py`**: Contains unit and integration tests for the entire pipeline, ensuring that intent classification, filtering, and formatting work correctly.
-   **`ml_demo.py`**: Provides a live demonstration of the AI capabilities with sample data and queries.

To run the tests:
```bash
python3 -m unittest test_ai_features.py
```

## Future Enhancements
-   Expand training data to cover more endpoints and query variations.
-   Introduce stateful awareness in interactive mode (e.g., remembering the last endpoint used).
-   Add support for more complex operations like data comparison or trend analysis.
-   Integrate with configuration backup and restore workflows.
