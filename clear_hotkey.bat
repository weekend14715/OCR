@echo off
chcp 65001 >nul
echo ================================================
echo        XOA PHIM TAT DA LUU
echo ================================================
echo.

REM Lấy đường dẫn thư mục config
set "CONFIG_DIR=%LOCALAPPDATA%\VietnameseOCRTool"
set "CONFIG_FILE=%CONFIG_DIR%\config.ini"

echo [INFO] Dang kiem tra thu muc config...
if not exist "%CONFIG_DIR%" (
    echo [WARNING] Thu muc config khong ton tai: %CONFIG_DIR%
    echo [INFO] Co the ban chua su dung phim tat bao gio.
    pause
    exit /b 1
)

echo [OK] Tim thay thu muc config: %CONFIG_DIR%
echo.

REM Kiểm tra file config.ini
if not exist "%CONFIG_FILE%" (
    echo [WARNING] File config.ini khong ton tai: %CONFIG_FILE%
    echo [INFO] Co the ban chua luu phim tat bao gio.
    pause
    exit /b 1
)

echo [OK] Tim thay file config.ini
echo.

REM Hiển thị nội dung file config hiện tại
echo [INFO] Noi dung file config hien tai:
echo ----------------------------------------
type "%CONFIG_FILE%"
echo ----------------------------------------
echo.

REM Xác nhận xóa
set /p "confirm=Ban co chac chan muon xoa phim tat da luu? (y/n): "
if /i not "%confirm%"=="y" (
    echo [INFO] Huy bo thao tac.
    pause
    exit /b 0
)

echo.
echo [INFO] Dang xoa phim tat...

REM Xóa file config.ini
del "%CONFIG_FILE%" 2>nul
if errorlevel 1 (
    echo [ERROR] Khong the xoa file config.ini
    echo [INFO] Co the file dang duoc su dung boi ung dung khac.
    pause
    exit /b 1
)

echo [OK] Da xoa file config.ini thanh cong!

REM Kiểm tra xem thư mục có còn file nào khác không
dir "%CONFIG_DIR%" /b 2>nul | findstr /v "config.ini" >nul
if errorlevel 1 (
    echo [INFO] Thu muc config da trong, dang xoa thu muc...
    rmdir "%CONFIG_DIR%" 2>nul
    if not errorlevel 1 (
        echo [OK] Da xoa thu muc config thanh cong!
    ) else (
        echo [WARNING] Khong the xoa thu muc config (co the con file khac).
    )
) else (
    echo [INFO] Thu muc config van con file khac, giu lai thu muc.
)

echo.
echo ================================================
echo [SUCCESS] DA XOA PHIM TAT THANH CONG!
echo ================================================
echo.
echo [INFO] Cac thao tac da thuc hien:
echo - Xoa file config.ini chua phim tat
echo - Xoa thu muc config neu trong
echo.
echo [INFO] Lan chay tiep theo, ung dung se yeu cau chon phim tat moi.
echo.
pause
