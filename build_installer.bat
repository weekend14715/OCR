@echo off
REM ============================================
REM Build Installer với Inno Setup
REM ============================================
chcp 65001 > nul
echo.
echo ============================================
echo   Vietnamese OCR Tool - Installer Builder
echo ============================================
echo.

REM Kiểm tra quyền admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Script cần quyền Administrator!
    echo    Right-click và chọn "Run as administrator"
    echo.
    pause
    exit /b 1
)

REM Chạy PowerShell script
powershell -ExecutionPolicy Bypass -File "build_installer.ps1"

if %errorLevel% neq 0 (
    echo.
    echo ❌ Build thất bại!
    echo.
    pause
    exit /b 1
)

echo.
pause

