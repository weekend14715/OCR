@echo off
chcp 65001 >nul
color 0A

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║        📖 VIEW DEPLOYMENT DOCUMENTATION                        ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo.
echo 📚 Available Documentation:
echo.
echo    1. START_DEPLOYMENT.txt           - BẮT ĐẦU TỪ ĐÂY!
echo    2. QUICK_DEPLOY_GUIDE.txt         - Quick start (10 phút)
echo    3. DEPLOY_RENDER.md               - Chi tiết đầy đủ
echo    4. DEPLOYMENT_CHECKLIST.md        - Checklist hoàn chỉnh
echo    5. setup_env_vars.txt             - Environment variables
echo    6. _DEPLOYMENT_FILES_CREATED.txt  - Files summary
echo    7. RENDER_DEPLOYMENT_COMPLETE.txt - Tổng kết
echo.
echo    0. Exit
echo.
echo ════════════════════════════════════════════════════════════════
echo.

set /p choice="Chọn file để xem (0-7): "

if "%choice%"=="1" (
    cls
    type START_DEPLOYMENT.txt
    echo.
    echo ════════════════════════════════════════════════════════════════
    pause
    goto :EOF
)

if "%choice%"=="2" (
    cls
    type QUICK_DEPLOY_GUIDE.txt
    echo.
    echo ════════════════════════════════════════════════════════════════
    pause
    goto :EOF
)

if "%choice%"=="3" (
    cls
    echo Opening DEPLOY_RENDER.md in default editor...
    start DEPLOY_RENDER.md
    goto :EOF
)

if "%choice%"=="4" (
    cls
    echo Opening DEPLOYMENT_CHECKLIST.md in default editor...
    start DEPLOYMENT_CHECKLIST.md
    goto :EOF
)

if "%choice%"=="5" (
    cls
    type setup_env_vars.txt
    echo.
    echo ════════════════════════════════════════════════════════════════
    pause
    goto :EOF
)

if "%choice%"=="6" (
    cls
    type _DEPLOYMENT_FILES_CREATED.txt
    echo.
    echo ════════════════════════════════════════════════════════════════
    pause
    goto :EOF
)

if "%choice%"=="7" (
    cls
    type RENDER_DEPLOYMENT_COMPLETE.txt
    echo.
    echo ════════════════════════════════════════════════════════════════
    pause
    goto :EOF
)

if "%choice%"=="0" (
    goto :EOF
)

echo.
echo ❌ Invalid choice!
pause

