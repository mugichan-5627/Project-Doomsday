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

# Launch the API server and the dashboard
echo "Starting Forecasting Track API on port 8000 in background..."
uvicorn api:app --host 0.0.0.0 --port 8000 &
API_PID=$!

echo "Launching Project Doomsday Streamlit Dashboard (Port 8501)..."
streamlit run app.py

# Auto-cleanup on exit
echo "Cleaning up background services..."
kill $API_PID 2>/dev/null
