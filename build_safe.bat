@echo off
chcp 65001 >nul
echo ============================================================
echo   Vietnamese OCR Tool - Safe Build (Tránh Windows Defender)
echo ============================================================
echo.
echo Script này build với các tùy chọn giúp tránh false positive
echo từ Windows Defender:
echo   - Tắt UPX compression (nguyên nhân chính)
echo   - Tối ưu hóa các tham số build
echo.
echo ============================================================
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python chưa được cài đặt hoặc chưa thêm vào PATH!
    echo.
    echo Vui lòng cài đặt Python từ: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [1/6] Checking Python... OK
echo.

REM Clean old builds
echo [2/6] Cleaning old builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo      Done!
echo.

REM Check icon.png
echo [3/6] Checking icon files...
if not exist icon.png (
    echo [WARNING] icon.png not found! Trying to create...
    if exist app_icon.ico (
        python create_icon.py
        if errorlevel 1 (
            echo [ERROR] Cannot create icon.png
            echo Please create it manually or ensure app_icon.ico exists
            pause
            exit /b 1
        )
    ) else (
        echo [ERROR] app_icon.ico not found!
        pause
        exit /b 1
    )
)
echo      Icons OK!
echo.

REM Install dependencies
echo [4/6] Installing Python dependencies...
pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)
echo      Done!
echo.

REM Build with PyInstaller (SAFE MODE - NO UPX)
echo [5/6] Building with PyInstaller (Safe Mode - No UPX)...
echo      This may take a few minutes...
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
    echo [ERROR] PyInstaller build failed!
    echo.
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo      Build successful!
echo.

REM Check output
echo [6/6] Verifying output...
if exist "dist\ocr_tool\ocr_tool.exe" (
    echo      ✓ EXE file created successfully!
    echo.
    echo ============================================================
    echo   BUILD COMPLETED SUCCESSFULLY!
    echo ============================================================
    echo.
    echo Output location: dist\ocr_tool\ocr_tool.exe
    echo.
    echo QUAN TRỌNG - Về Windows Defender:
    echo.
    echo 1. Nếu Windows Defender vẫn chặn file:
    echo    - Đây là FALSE POSITIVE (cảnh báo sai)
    echo    - File này an toàn 100%%
    echo.
    echo 2. Cách khắc phục:
    echo    a. Mở Windows Security
    echo    b. Virus ^& threat protection
    echo    c. Exclusions → Add exclusion → Folder
    echo    d. Chọn thư mục: %CD%
    echo.
    echo 3. Hoặc chạy lệnh PowerShell (as Admin):
    echo    Add-MpPreference -ExclusionPath "%CD%"
    echo.
    echo 4. Đọc chi tiết: FIX_WINDOWS_DEFENDER.md
    echo.
    echo ============================================================
    echo.
    echo Bạn có muốn build installer với Inno Setup? (Y/N)
    set /p build_installer="Chọn (Y/N): "
    
    if /i "%build_installer%"=="Y" (
        echo.
        echo Building installer with Inno Setup...
        
        REM Kiểm tra Inno Setup
        if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
            "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
            if errorlevel 1 (
                echo [ERROR] Inno Setup build failed!
            ) else (
                echo.
                echo ============================================================
                echo   INSTALLER CREATED SUCCESSFULLY!
                echo ============================================================
                echo.
                echo File: Output\VietnameseOCRTool_Setup.exe
                echo.
                echo LƯU Ý: Installer cũng có thể bị Windows Defender chặn.
                echo Làm theo hướng dẫn trong FIX_WINDOWS_DEFENDER.md
                echo.
            )
        ) else (
            echo [ERROR] Inno Setup not found!
            echo Please install from: https://jrsoftware.org/isdl.php
            echo Or build installer manually: "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
        )
    )
) else (
    echo [ERROR] Build failed - EXE file not found!
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo.
pause
exit /b 0

