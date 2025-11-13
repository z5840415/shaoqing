@echo off
chcp 65001 >nul
REM 达人猎手 - 快速启动脚本 (Windows)

echo ======================================
echo   达人猎手 - 启动中...
echo ======================================

REM 检查Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js未安装，请先安装Node.js
    pause
    exit /b 1
)

REM 检查Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python未安装，请先安装Python
    pause
    exit /b 1
)

REM 检查依赖
if not exist "node_modules" (
    echo 📦 首次运行，正在安装Node.js依赖...
    call npm install
)

if not exist "backend\venv" (
    echo 📦 首次运行，正在创建Python虚拟环境...
    cd backend
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    playwright install chromium
    cd ..
)

REM 启动应用
echo 🚀 启动达人猎手...
npm start
