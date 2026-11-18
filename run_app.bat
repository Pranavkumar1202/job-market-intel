@echo off
cd /d %~dp0
call .venv\Scripts\activate.bat
echo Starting the API (this loads the model, about 20 seconds)...
start "Job Market API" cmd /k "uvicorn src.api.main:app"
timeout /t 25 /nobreak > nul
echo Starting the dashboard...
start "Job Market Dashboard" cmd /k "streamlit run ui/streamlit_app.py"
