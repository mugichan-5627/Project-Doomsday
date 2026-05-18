@echo off
rem Project Doomsday - Standardized Run Script for Windows
echo =====================================================
echo Initializing Project Doomsday Standardized Environment...
echo =====================================================

rem Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

rem Activate virtual environment
call venv\Scripts\activate.bat

rem Upgrade pip and install dependencies
echo Installing dependencies from requirements.txt...
python -m pip install --upgrade pip
pip install -r requirements.txt

rem Create .env from template if it doesn't exist
if not exist .env (
    echo Creating .env configuration file from template...
    copy .env.example .env
    echo WARNING: Created a new .env file. Please edit it to add your API keys.
)

rem Launch the API server and the dashboard
echo Launching Project Doomsday API Server in a new window (Port 8000)...
start "Project Doomsday API" cmd /k "call venv\Scripts\activate.bat && uvicorn api:app --host 0.0.0.0 --port 8000"

echo Launching Project Doomsday Streamlit Dashboard (Port 8501)...
streamlit run app.py
pause
