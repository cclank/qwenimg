#!/bin/bash

echo "🚀 QwenImg 启动"
echo ""

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 配置检查
if [ -z "$DASHSCOPE_API_KEY" ]; then
    echo "❌ 请先设置 API Key："
    echo "   export DASHSCOPE_API_KEY=\"your-key\""
    exit 1
fi

# 创建日志目录
mkdir -p logs

# 启动后端
echo "启动后端..."
cd backend
python run.py > ../logs/backend.log 2>&1 &
echo $! > ../logs/backend.pid
cd ..

sleep 2

# 启动前端
echo "启动前端..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
echo $! > ../logs/frontend.pid
cd ..

echo ""
echo "✅ 服务已启动"
echo ""
echo "前端: http://localhost:3000"
echo "后端: http://localhost:8000"
echo ""
echo "查看日志:"
echo "  后端: tail -f logs/backend.log"
echo "  前端: tail -f logs/frontend.log"
echo ""
echo "停止服务: ./stop_dev.sh"
echo ""
