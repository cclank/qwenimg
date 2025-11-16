#!/bin/bash

# QwenImg 开发环境启动脚本

echo "╔═══════════════════════════════════════════════════════╗"
echo "║     QwenImg AI 创作平台 - 开发环境启动               ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# 检查是否在项目根目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3，请先安装Python"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误：未找到Node.js，请先安装Node.js"
    exit 1
fi

# 检查后端依赖
echo "📦 检查后端依赖..."
if [ ! -f "backend/.env" ]; then
    echo "⚠️  警告：未找到backend/.env文件，从示例复制..."
    cp backend/.env.example backend/.env
    echo "⚠️  请编辑 backend/.env 文件，填入你的API Key"
fi

# 检查前端依赖
echo "📦 检查前端依赖..."
if [ ! -d "frontend/node_modules" ]; then
    echo "📥 安装前端依赖..."
    cd frontend && npm install && cd ..
fi

# 创建日志目录
mkdir -p logs

# 启动后端
echo ""
echo "🚀 启动后端服务..."
cd backend
python3 run.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo "✅ 后端已启动 (PID: $BACKEND_PID)"
echo "📄 后端日志: logs/backend.log"

# 等待后端启动
echo "⏳ 等待后端启动..."
sleep 3

# 启动前端
echo ""
echo "🚀 启动前端服务..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "✅ 前端已启动 (PID: $FRONTEND_PID)"
echo "📄 前端日志: logs/frontend.log"

# 保存PID
echo $BACKEND_PID > logs/backend.pid
echo $FRONTEND_PID > logs/frontend.pid

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║              🎉 启动成功！                            ║"
echo "╠═══════════════════════════════════════════════════════╣"
echo "║  前端地址: http://localhost:3000                      ║"
echo "║  后端地址: http://localhost:8000                      ║"
echo "║  API文档: http://localhost:8000/api/docs             ║"
echo "║                                                       ║"
echo "║  停止服务: ./stop_dev.sh                             ║"
echo "║  查看日志: tail -f logs/backend.log                  ║"
echo "║           tail -f logs/frontend.log                  ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# 等待用户输入
echo "按 Ctrl+C 停止服务..."
wait
