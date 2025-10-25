#!/bin/bash

# AeyeGuard MCP Service - Run Script
# Simple script to run the service (assumes setup is already done)

echo "Starting AeyeGuard MCP Service..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run './setup_and_run.sh' first to set up the environment."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Using default configuration."
    echo "To customize settings, copy .env.example to .env"
    echo ""
fi

# Activate virtual environment
source venv/bin/activate

# Run the service
echo "Press Ctrl+C to stop the service"
echo ""
python -m src.AeyeGuard_mcp
