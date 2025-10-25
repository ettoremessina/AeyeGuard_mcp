#!/bin/bash

# AeyeGuard MCP Service - Setup and Run Script
# This script sets up the environment from scratch and runs the service

echo "AeyeGuard MCP Service - Setup and Run"
echo "======================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "Please edit .env to configure your settings."
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Warning: Virtual environment not found."
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Checking dependencies..."
pip install -q -r requirements.txt

echo ""
echo "Starting MCP service..."
echo "Press Ctrl+C to stop"
echo ""

# Run the service
python -m src.AeyeGuard_mcp
