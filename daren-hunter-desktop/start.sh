#!/bin/bash

# 达人猎手 - 快速启动脚本 (Linux/macOS)

echo "======================================"
echo "  达人猎手 - 启动中..."
echo "======================================"

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js未安装，请先安装Node.js"
    exit 1
fi

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python3"
    exit 1
fi

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "📦 首次运行，正在安装Node.js依赖..."
    npm install
fi

if [ ! -d "backend/venv" ]; then
    echo "📦 首次运行，正在创建Python虚拟环境..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    playwright install chromium
    cd ..
else
    cd backend
    source venv/bin/activate
    cd ..
fi

# 启动应用
echo "🚀 启动达人猎手..."
npm start
