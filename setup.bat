@echo off
echo ========================================
echo E2E Automation Framework - Setup Script
echo ========================================
echo.

REM
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/5] Installing Playwright browsers...
playwright install chromium
if errorlevel 1 (
    echo Warning: Failed to install Playwright browsers
)

echo [5/5] Creating .env file...
if not exist .env (
    copy .env.example .env
    echo Created .env file. Please edit it if needed.
) else (
    echo .env file already exists.
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To run tests, use:
echo   venv\Scripts\activate
echo   pytest tests/ -v
echo.
echo To generate Allure report:
echo   pytest tests/ -v --alluredir=allure-results
echo   allure serve allure-results
echo.
pause
