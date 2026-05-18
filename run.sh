#!/bin/bash
# Project Doomsday - Standardized Run Script for Unix/Linux/Mac
echo "====================================================="
echo "Initializing Project Doomsday Standardized Environment..."
echo "====================================================="

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate

# Upgrade pip and install dependencies
echo "Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env from template if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env configuration file from template..."
    cp .env.example .env
    echo "WARNING: Created a new .env file. Please edit it to add your API keys."
fi

# Launch the dashboard
echo "Launching Project Doomsday..."
streamlit run app.py
