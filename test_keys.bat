@echo off
chcp 65001 >nul
title License Key Tester

echo ========================================
echo    LICENSE KEY TESTER & MANAGER
echo ========================================
echo.

:menu
echo Chọn tùy chọn:
echo 1. Clear license hiện tại
echo 2. Test một key cụ thể
echo 3. Test keys mẫu
echo 4. Hiển thị license hiện tại
echo 5. Chạy menu tương tác đầy đủ
echo 0. Thoát
echo.

set /p choice="Nhập lựa chọn (0-5): "

if "%choice%"=="1" (
    echo.
    echo Đang clear license...
    python test_license_keys.py clear
    pause
    goto menu
)

if "%choice%"=="2" (
    echo.
    set /p key="Nhập license key để test: "
    if not "%key%"=="" (
        python quick_test_keys.py "%key%"
    ) else (
        echo Không có key nào được nhập!
    )
    pause
    goto menu
)

if "%choice%"=="3" (
    echo.
    echo Đang test keys mẫu...
    python test_license_keys.py
    pause
    goto menu
)

if "%choice%"=="4" (
    echo.
    python test_license_keys.py show
    pause
    goto menu
)

if "%choice%"=="5" (
    echo.
    python test_license_keys.py
    pause
    goto menu
)

if "%choice%"=="0" (
    echo Tạm biệt!
    exit
)

echo Lựa chọn không hợp lệ!
pause
goto menu
