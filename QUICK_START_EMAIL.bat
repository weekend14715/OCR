@echo off
chcp 65001 >nul
cls

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║       🚀 QUICK START - EMAIL SYSTEM TEST                      ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo 📧 Test hệ thống email OCR Tool License
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Lỗi: Không tìm thấy Python!
    echo.
    echo Cài Python từ: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python đã cài đặt
echo.

:: Check email_config.py
if not exist "license_server\email_config.py" (
    echo ❌ Lỗi: Chưa có file email_config.py
    echo.
    echo Hướng dẫn:
    echo   1. Copy file: license_server\email_config.example.py
    echo   2. Đổi tên thành: email_config.py
    echo   3. Điền thông tin email và App Password
    echo.
    pause
    exit /b 1
)

echo ✅ File email_config.py đã tồn tại
echo.

:: Run test
echo ═══════════════════════════════════════════════════════════════
echo.
echo 🧪 Đang chạy test email...
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

python test_email_config.py

echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo ✅ Hoàn tất!
echo.
echo 📖 Đọc thêm: EMAIL_SYSTEM_GUIDE.md
echo.
pause

