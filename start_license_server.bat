@echo off
echo ============================================
echo Vietnamese OCR Tool - License Server
echo ============================================
echo.

cd license_server

echo Checking dependencies...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting license server...
echo Server URL: http://127.0.0.1:5000
echo Admin Panel: http://127.0.0.1:5000/admin
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause

