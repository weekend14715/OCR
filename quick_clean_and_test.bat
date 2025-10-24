@echo off
chcp 65001 >nul
title Quick Clean & Test License
color 0B

echo.
echo ========================================================================
echo   🚀 QUICK CLEAN & TEST - Xóa license và test key mới
echo ========================================================================
echo.

:: Clean license
echo [1/2] Đang xóa license cũ...
echo.

if exist ".lic" (
    del /f /q ".lic" 2>nul
    echo     ✅ Đã xóa: .lic
) else (
    echo     ℹ️  File .lic không tồn tại
)

reg delete "HKCU\Software\OCRTool" /f >nul 2>&1
if %errorLevel% == 0 (
    echo     ✅ Đã xóa: Registry
) else (
    echo     ℹ️  Registry không tồn tại
)

if exist "%APPDATA%\OCRTool\.checksum" (
    del /f /q "%APPDATA%\OCRTool\.checksum" 2>nul
    echo     ✅ Đã xóa: Backup checksum
) else (
    echo     ℹ️  Backup không tồn tại
)

echo.
echo     🎉 Clean hoàn tất!
echo.

:: Pause để user xem
timeout /t 2 >nul

:: Test với license key mới
echo [2/2] Mở dialog để nhập license key mới...
echo.
echo     💡 Nhập license key của bạn vào dialog sẽ hiện
echo.

:: Chạy test license
python test_license_real_key.py

echo.
echo ========================================================================
echo   ✅ HOÀN TẤT!
echo ========================================================================
echo.
pause

