#!/bin/bash

# QwenImg 开发环境停止脚本

echo "🛑 停止 QwenImg 开发服务..."

# 检查PID文件
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        echo "⏹️  停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        echo "✅ 后端已停止"
    fi
    rm logs/backend.pid
fi

if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "⏹️  停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        echo "✅ 前端已停止"
    fi
    rm logs/frontend.pid
fi

# 清理可能的残留进程
pkill -f "uvicorn app.main:app" 2>/dev/null
pkill -f "vite" 2>/dev/null

echo "✅ 所有服务已停止"
