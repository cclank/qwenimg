#!/bin/bash

# 快速测试脚本 - 仅启动前端用于测试

echo "🧪 启动前端测试..."

# 检查依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 安装前端依赖..."
    cd frontend && npm install && cd ..
fi

echo "🚀 启动前端..."
cd frontend && npm run dev
