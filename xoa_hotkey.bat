@echo off
chcp 65001 >nul
echo ====================================
echo   XÓA CẤU HÌNH HOTKEY
echo ====================================
echo.

set CONFIG_PATH=%LOCALAPPDATA%\VietnameseOCRTool\config.ini

if exist "%CONFIG_PATH%" (
    del "%CONFIG_PATH%"
    echo ✓ Đã xóa file config.ini
    echo.
    echo Đường dẫn: %CONFIG_PATH%
    echo.
    echo Lần chạy chương trình tiếp theo sẽ hiển thị
    echo giao diện chọn hotkey mới!
) else (
    echo ✗ File config.ini không tồn tại
    echo.
    echo Đường dẫn kiểm tra: %CONFIG_PATH%
)

echo.
echo ====================================
pause

