@echo off
chcp 65001 >nul
title Clean License - Xóa Toàn Bộ License Data
color 0E

echo.
echo ========================================================================
echo   🧹 CLEAN LICENSE TOOL - XÓA DỮ LIỆU LICENSE
echo ========================================================================
echo.
echo   Công cụ này sẽ xóa toàn bộ dữ liệu license từ 3 vị trí:
echo   [1] File .lic
echo   [2] Registry (HKCU\Software\OCRTool)
echo   [3] Backup checksum (%%APPDATA%%\OCRTool)
echo.
echo   Sau khi xóa, bạn có thể test với license key mới.
echo.
echo ========================================================================
echo.

:: Kiểm tra quyền admin (optional, vì HKCU không cần admin)
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] Running with Administrator privileges
) else (
    echo [!] Running without Admin (OK for HKCU registry)
)
echo.

:: Xác nhận
set /p confirm="Bạn có chắc muốn XÓA toàn bộ license? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo.
    echo ❌ Đã hủy. Không có gì bị xóa.
    echo.
    pause
    exit /b
)

echo.
echo ========================================================================
echo   BẮT ĐẦU XÓA DỮ LIỆU...
echo ========================================================================
echo.

:: ============================================================================
:: BƯỚC 1: XÓA FILE .lic
:: ============================================================================
echo [1/3] Xóa file .lic trong thư mục hiện tại...

if exist ".lic" (
    del /f /q ".lic" 2>nul
    if exist ".lic" (
        echo     ❌ Không thể xóa .lic (file đang được sử dụng?)
    ) else (
        echo     ✅ Đã xóa: .lic
    )
) else (
    echo     ℹ️  File .lic không tồn tại
)

:: Thử xóa ở thư mục khác (nếu có)
if exist "%~dp0.lic" (
    del /f /q "%~dp0.lic" 2>nul
    if not exist "%~dp0.lic" (
        echo     ✅ Đã xóa: %~dp0.lic
    )
)

echo.

:: ============================================================================
:: BƯỚC 2: XÓA REGISTRY
:: ============================================================================
echo [2/3] Xóa Registry keys (HKCU\Software\OCRTool)...

:: Kiểm tra key có tồn tại không
reg query "HKCU\Software\OCRTool" >nul 2>&1
if %errorLevel% == 0 (
    :: Xóa toàn bộ key
    reg delete "HKCU\Software\OCRTool" /f >nul 2>&1
    if %errorLevel% == 0 (
        echo     ✅ Đã xóa: HKCU\Software\OCRTool
        echo        - InstallID
        echo        - Checksum
        echo        - Hash
    ) else (
        echo     ❌ Không thể xóa registry key
    )
) else (
    echo     ℹ️  Registry key không tồn tại
)

echo.

:: ============================================================================
:: BƯỚC 3: XÓA BACKUP CHECKSUM
:: ============================================================================
echo [3/3] Xóa backup checksum (%%APPDATA%%\OCRTool)...

set APPDATA_PATH=%APPDATA%\OCRTool

if exist "%APPDATA_PATH%\.checksum" (
    del /f /q "%APPDATA_PATH%\.checksum" 2>nul
    if exist "%APPDATA_PATH%\.checksum" (
        echo     ❌ Không thể xóa .checksum
    ) else (
        echo     ✅ Đã xóa: %APPDATA_PATH%\.checksum
    )
) else (
    echo     ℹ️  File .checksum không tồn tại
)

:: Xóa thư mục nếu rỗng
if exist "%APPDATA_PATH%" (
    rmdir "%APPDATA_PATH%" 2>nul
    if not exist "%APPDATA_PATH%" (
        echo     ✅ Đã xóa thư mục: %APPDATA_PATH%
    )
)

echo.

:: ============================================================================
:: KIỂM TRA KẾT QUẢ
:: ============================================================================
echo ========================================================================
echo   KIỂM TRA KẾT QUẢ
echo ========================================================================
echo.

set ALL_CLEAN=1

:: Check file .lic
if exist ".lic" (
    echo [❌] File .lic vẫn còn
    set ALL_CLEAN=0
) else (
    echo [✓] File .lic đã bị xóa
)

:: Check registry
reg query "HKCU\Software\OCRTool" >nul 2>&1
if %errorLevel% == 0 (
    echo [❌] Registry key vẫn còn
    set ALL_CLEAN=0
) else (
    echo [✓] Registry key đã bị xóa
)

:: Check backup
if exist "%APPDATA_PATH%\.checksum" (
    echo [❌] Backup checksum vẫn còn
    set ALL_CLEAN=0
) else (
    echo [✓] Backup checksum đã bị xóa
)

echo.
echo ========================================================================

if "%ALL_CLEAN%"=="1" (
    echo   ✅ HOÀN TẤT! Đã xóa sạch toàn bộ license data
    echo.
    echo   Bây giờ bạn có thể:
    echo   1. Test với license key mới
    echo   2. Activate lại với key cũ
    echo   3. Chạy app sẽ hiện dialog nhập license
) else (
    echo   ⚠️  MỘT SỐ FILE CHƯA XÓA ĐƯỢC
    echo.
    echo   Nguyên nhân có thể:
    echo   - File đang được mở bởi ứng dụng
    echo   - Thiếu quyền truy cập
    echo.
    echo   Giải pháp:
    echo   1. Đóng tất cả ứng dụng OCR Tool
    echo   2. Chạy lại batch file này
)

echo ========================================================================
echo.
pause

