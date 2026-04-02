@echo off
chcp 65001 >nul
echo ====================================
echo   战术视界 - 后端开发服务器
echo ====================================
echo.

cd /d "%~dp0backend"

echo 正在停止现有的后端服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo 正在停止进程 %%a...
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo 正在启动后端服务...
echo.
python run.py

pause
