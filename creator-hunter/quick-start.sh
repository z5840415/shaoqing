#!/bin/bash

echo "=========================================="
echo "  Creator Hunter 快速启动脚本"
echo "=========================================="
echo ""

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    echo "   安装指南: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

echo "✅ Docker已安装: $(docker --version)"
echo "✅ Docker Compose已安装: $(docker-compose --version)"
echo ""

# 检查.env文件
if [ ! -f .env ]; then
    echo "📝 创建.env配置文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件配置必要的参数"
    echo ""
    read -p "是否现在编辑配置文件？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} .env
    fi
fi

echo ""
echo "🚀 启动所有服务..."
echo ""

# 启动服务
docker-compose up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "  ✅ 启动成功！"
    echo "=========================================="
    echo ""
    echo "📱 访问地址："
    echo "  前端管理界面: http://localhost:3000"
    echo "  后端API:      http://localhost:8000"
    echo "  API文档:      http://localhost:8000/docs"
    echo ""
    echo "📊 查看容器状态："
    echo "  docker-compose ps"
    echo ""
    echo "📋 查看日志："
    echo "  docker-compose logs -f"
    echo ""
    echo "🛑 停止服务："
    echo "  docker-compose down"
    echo ""
    echo "=========================================="
else
    echo ""
    echo "❌ 启动失败，请检查错误信息"
    echo ""
    echo "查看日志："
    echo "  docker-compose logs"
fi
