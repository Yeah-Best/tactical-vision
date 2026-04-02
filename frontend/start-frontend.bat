@echo off
REM 清除 DNS 缓存
ipconfig /flushdns >nul 2>&1

REM 强制 Node.js 使用 IPv4
set NODE_OPTIONS=--enable-source-maps
set HOST=127.0.0.1

chcp 65001 >nul
echo ====================================
echo   战术视界 - 前端开发服务器
echo ====================================
echo.
echo 访问地址:
echo   - http://localhost:5173
echo   - http://127.0.0.1:5173
echo   - http://192.168.192.1:5173 (网络访问)
echo.
echo 按 Ctrl+C 停止服务
echo ====================================
echo.

cd /d "%~dp0"
node node_modules\vite\bin\vite.js --host 127.0.0.1 --port 5173

