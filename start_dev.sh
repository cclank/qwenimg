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

# 检查API Key环境变量
echo "🔑 检查API Key配置..."
if [ -z "$DASHSCOPE_API_KEY" ]; then
    if [ -f ".env" ]; then
        echo "⚠️  警告：未设置 DASHSCOPE_API_KEY 环境变量"
        echo "    将使用 .env 文件中的配置"
    else
        echo "⚠️  警告：未设置 DASHSCOPE_API_KEY 环境变量且未找到 .env 文件"
        echo "    正在从示例复制 .env 文件..."
        cp .env.example .env
        echo ""
        echo "❌ 请先配置API Key："
        echo "   方式1（推荐）：export DASHSCOPE_API_KEY=\"your_api_key\""
        echo "   方式2：编辑项目根目录的 .env 文件"
        echo ""
        exit 1
    fi
else
    echo "✅ API Key已配置"
fi

# 检查并安装后端依赖
echo ""
echo "📦 检查Python依赖..."

# 检查是否有虚拟环境
if [ -d "venv" ]; then
    echo "✅ 发现虚拟环境，激活中..."
    source venv/bin/activate
fi

# 检查uvicorn是否已安装
if ! python3 -c "import uvicorn" 2>/dev/null; then
    echo "📥 安装Python依赖（从根目录）..."
    if ! pip3 install -r requirements.txt; then
        echo "❌ Python依赖安装失败"
        echo "   请手动运行："
        echo "   pip3 install -r requirements.txt"
        exit 1
    fi
    echo "✅ Python依赖安装成功"
else
    echo "✅ Python依赖已安装"
fi

# 检查并安装前端依赖
echo ""
echo "📦 检查前端依赖..."
if [ ! -d "frontend/node_modules" ]; then
    echo "📥 安装前端依赖..."
    cd frontend
    if ! npm install; then
        echo "❌ 前端依赖安装失败"
        echo "   请手动运行："
        echo "   cd frontend && npm install"
        exit 1
    fi
    cd ..
    echo "✅ 前端依赖安装成功"
else
    echo "✅ 前端依赖已安装"
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

# 保存PID
echo $BACKEND_PID > logs/backend.pid

echo "⏳ 等待后端启动..."
sleep 3

# 检查后端是否启动成功
if ! ps -p $BACKEND_PID > /dev/null; then
    echo ""
    echo "❌ 后端启动失败！"
    echo "📄 错误日志："
    echo "----------------------------------------"
    tail -20 logs/backend.log
    echo "----------------------------------------"
    echo ""
    echo "💡 常见问题："
    echo "   1. 检查是否安装了所有依赖: cd backend && pip3 install -r requirements.txt"
    echo "   2. 检查端口8000是否被占用: lsof -i :8000"
    echo "   3. 检查API Key是否配置正确"
    echo "   4. 查看完整日志: cat logs/backend.log"
    exit 1
fi

# 检查后端HTTP服务是否可访问
echo "🔍 验证后端服务..."
MAX_RETRIES=10
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ 后端服务已就绪 (PID: $BACKEND_PID)"
        echo "📄 后端日志: logs/backend.log"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo ""
        echo "⚠️  警告：后端服务启动但无法访问"
        echo "📄 请检查日志: tail -f logs/backend.log"
        echo ""
    fi
    sleep 1
done

# 启动前端
echo ""
echo "🚀 启动前端服务..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# 保存PID
echo $FRONTEND_PID > logs/frontend.pid

echo "⏳ 等待前端启动..."
sleep 3

# 检查前端是否启动成功
if ! ps -p $FRONTEND_PID > /dev/null; then
    echo ""
    echo "❌ 前端启动失败！"
    echo "📄 错误日志："
    echo "----------------------------------------"
    tail -20 logs/frontend.log
    echo "----------------------------------------"
    echo ""
    echo "💡 常见问题："
    echo "   1. 检查是否安装了依赖: cd frontend && npm install"
    echo "   2. 检查端口3000是否被占用: lsof -i :3000"
    echo "   3. 查看完整日志: cat logs/frontend.log"
    echo ""
    echo "🛑 停止后端服务..."
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
echo "📄 前端日志: logs/frontend.log"

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
