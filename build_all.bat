@echo off
REM ====================================================================
REM Build Script cho Vietnamese OCR Tool
REM Script này tự động hóa quá trình build và đóng gói ứng dụng
REM ====================================================================

echo ========================================
echo Vietnamese OCR Tool - Build Script
echo ========================================
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python chua duoc cai dat!
    echo Vui long cai dat Python 3.8 tro len.
    pause
    exit /b 1
)
echo [OK] Python da duoc cai dat

REM Kiểm tra PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [WARNING] PyInstaller chua duoc cai dat
    echo Dang cai dat PyInstaller...
    pip install pyinstaller
)
echo [OK] PyInstaller san sang

REM Cài đặt dependencies
echo.
echo [STEP 1/5] Cai dat cac thu vien can thiet...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Khong the cai dat dependencies!
    pause
    exit /b 1
)
echo [OK] Da cai dat xong cac thu vien

REM Tạo icon.png nếu chưa có
echo.
echo [STEP 2/5] Kiem tra file icon...
if not exist "icon.png" (
    echo [WARNING] icon.png khong ton tai
    if exist "app_icon.ico" (
        echo Dang chuyen doi app_icon.ico sang icon.png...
        python -c "from PIL import Image; img = Image.open('app_icon.ico'); img.save('icon.png')"
        if errorlevel 1 (
            echo [ERROR] Khong the chuyen doi icon!
            echo Vui long tao file icon.png thu cong.
            pause
            exit /b 1
        )
        echo [OK] Da tao icon.png thanh cong
    ) else (
        echo [ERROR] Khong tim thay app_icon.ico hoac icon.png!
        pause
        exit /b 1
    )
) else (
    echo [OK] icon.png da ton tai
)

REM Build với PyInstaller
echo.
echo [STEP 3/5] Dong goi Python thanh EXE...
pyinstaller --name="ocr_tool" --onedir --windowed --icon="app_icon.ico" --add-data="icon.png;." --hidden-import="PIL._tkinter_finder" --clean ocr_tool.py
if errorlevel 1 (
    echo [ERROR] Build that bai!
    pause
    exit /b 1
)
echo [OK] Build thanh cong!

REM Kiểm tra Tesseract-OCR
echo.
echo [STEP 4/5] Kiem tra Tesseract-OCR...
if not exist "Tesseract-OCR" (
    echo [WARNING] Thu muc Tesseract-OCR khong ton tai!
    echo.
    echo Ban co 2 lua chon:
    echo 1. Copy tu cai dat hien tai (C:\Program Files\Tesseract-OCR)
    echo 2. Huy va chuan bi thu cong
    echo.
    choice /C 12 /M "Chon lua chon"
    if errorlevel 2 goto :manual_tesseract
    if errorlevel 1 goto :copy_tesseract
    
    :copy_tesseract
    if exist "C:\Program Files\Tesseract-OCR" (
        echo Dang copy Tesseract-OCR...
        xcopy "C:\Program Files\Tesseract-OCR" "Tesseract-OCR\" /E /I /H /Y
        echo [OK] Da copy Tesseract-OCR
    ) else (
        echo [ERROR] Khong tim thay Tesseract-OCR o C:\Program Files\
        goto :manual_tesseract
    )
    
) else (
    echo [OK] Tesseract-OCR da san sang
)
goto :check_vie_data

:manual_tesseract
echo.
echo Vui long:
echo 1. Tai Tesseract tu: https://github.com/UB-Mannheim/tesseract/wiki
echo 2. Giai nen vao thu muc "Tesseract-OCR"
echo 3. Chay lai script nay
pause
exit /b 1

:check_vie_data
REM Kiểm tra file dữ liệu tiếng Việt
if not exist "tesseract-main\tessdata\vie.traineddata" (
    echo [WARNING] Khong tim thay vie.traineddata!
    echo Vui long dam bao file nay ton tai de ho tro tieng Viet.
)

REM Build Inno Setup
echo.
echo [STEP 5/5] Tao installer voi Inno Setup...

REM Tìm Inno Setup
set "INNO_PATH="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "INNO_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if "%INNO_PATH%"=="" (
    echo [WARNING] Khong tim thay Inno Setup!
    echo Vui long:
    echo 1. Cai dat Inno Setup 6 tu: https://jrsoftware.org/isdl.php
    echo 2. Mo file setup.iss bang Inno Setup va compile thu cong
    echo.
    echo Hoac mo file setup.iss de tao installer.
    start explorer setup.iss
    echo.
    echo [INFO] File EXE da duoc tao trong: dist\ocr_tool\
    pause
    exit /b 0
)

echo [OK] Tim thay Inno Setup
"%INNO_PATH%" setup.iss
if errorlevel 1 (
    echo [ERROR] Khong the tao installer!
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD HOAN THANH!
echo ========================================
echo.
echo File installer da duoc tao tai:
echo Output\VietnameseOCRTool_Setup.exe
echo.
echo Ban co the copy file nay sang may khac de cai dat.
echo.
pause
start explorer Output

