@echo off
chcp 65001 >nul
echo ╔═══════════════════════════════════════════════════════════╗
echo ║  Vietnamese OCR Tool - Rebuild After Adding Exclusion    ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo ⚠️  QUAN TRỌNG: Hãy đảm bảo bạn đã:
echo.
echo    1. Thêm folder F:\OCR\OCR vào Windows Defender Exclusions
echo    2. Hoặc tắt Real-time Protection tạm thời
echo.
echo ══════════════════════════════════════════════════════════
echo.
pause

echo.
echo [1/4] Cleaning old files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "F:\OCR\OCR\build\ocr_tool\ocr_tool.exe" del /f /q "F:\OCR\OCR\build\ocr_tool\ocr_tool.exe"
echo      Done!
echo.

echo [2/4] Verifying icon files...
if not exist icon.png (
    echo [ERROR] icon.png not found!
    pause
    exit /b 1
)
if not exist app_icon.ico (
    echo [ERROR] app_icon.ico not found!
    pause
    exit /b 1
)
echo      Icons OK!
echo.

echo [3/4] Building with PyInstaller (NO UPX - Safe Mode)...
echo      This will take a few minutes...
echo.

pyinstaller --clean ^
    --noconfirm ^
    --log-level=WARN ^
    --onedir ^
    --windowed ^
    --noupx ^
    --name "ocr_tool" ^
    --icon "app_icon.ico" ^
    --add-data "icon.png;." ^
    --add-data "app_icon.ico;." ^
    --hidden-import "PIL._tkinter_finder" ^
    --hidden-import "pystray._win32" ^
    ocr_tool.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo [4/4] Checking output...

if exist "dist\ocr_tool\ocr_tool.exe" (
    echo.
    echo ╔═══════════════════════════════════════════════════════════╗
    echo ║              ✅ BUILD SUCCESSFUL!                         ║
    echo ╚═══════════════════════════════════════════════════════════╝
    echo.
    echo 📁 Output: dist\ocr_tool\ocr_tool.exe
    echo.
    echo 🔍 Checking if Windows Defender still blocks...
    timeout /t 3 >nul
    
    REM Try to copy file to test if it's blocked
    copy "dist\ocr_tool\ocr_tool.exe" "dist\ocr_tool\ocr_tool_test.exe" >nul 2>&1
    if errorlevel 1 (
        echo.
        echo ⚠️  WARNING: File might still be blocked by Windows Defender!
        echo.
        echo Please:
        echo   1. Check Windows Security notifications
        echo   2. Make sure you added exclusion correctly
        echo   3. Try disabling Real-time Protection temporarily
        echo.
    ) else (
        del "dist\ocr_tool\ocr_tool_test.exe" >nul 2>&1
        echo.
        echo ✅ File looks good! Windows Defender is not blocking it.
        echo.
        echo You can now test the app:
        echo   dist\ocr_tool\ocr_tool.exe
        echo.
    )
) else (
    echo.
    echo [ERROR] Build failed - EXE not found!
    pause
    exit /b 1
)

echo.
echo ══════════════════════════════════════════════════════════
echo.
pause

