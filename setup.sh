#!/bin/bash

echo "========================================"
echo "E2E Automation Framework - Setup Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[1/5] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

echo "[2/5] Activating virtual environment..."
source venv/bin/activate

echo "[3/5] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo "[4/5] Installing Playwright browsers..."
playwright install chromium

echo "[5/5] Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please edit it if needed."
else
    echo ".env file already exists."
fi

echo ""
echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo ""
echo "To run tests, use:"
echo "  source venv/bin/activate"
echo "  pytest tests/ -v"
echo ""
echo "To generate Allure report:"
echo "  pytest tests/ -v --alluredir=allure-results"
echo "  allure serve allure-results"
echo ""
