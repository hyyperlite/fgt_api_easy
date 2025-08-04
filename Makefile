# Makefile for FortiGate API Generic Client

.PHONY: help install test clean examples

# Default target
help:
	@echo "FortiGate API Generic Client"
	@echo "============================"
	@echo ""
	@echo "Available targets:"
	@echo "  help     - Show this help message"
	@echo "  install  - Install required dependencies"
	@echo "  test     - Run the test suite"
	@echo "  examples - Show usage examples"
	@echo "  clean    - Clean up temporary files"
	@echo ""
	@echo "Usage examples:"
	@echo "  make install"
	@echo "  make test"
	@echo "  python3 fgt_api_client.py --help"

install:
	@echo "Installing dependencies..."
	python3 -m pip install --user git+https://github.com/p4r4n0y1ng/pyfgt.git requests
	@echo "✓ Dependencies installed"

test:
	@echo "Running test suite..."
	python3 test_client.py

examples:
	@echo "Running examples (configure HOST and API_KEY first)..."
	python3 examples.py

clean:
	@echo "Cleaning up temporary files..."
	rm -f test_config.ini test_config.json
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleanup complete"
