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

# 检查依赖（不自动安装）
echo ""
echo "📦 检查依赖..."

# 检查是否有虚拟环境并激活
if [ -d "venv" ]; then
    echo "✅ 发现虚拟环境，激活中..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "✅ 发现虚拟环境，激活中..."
    source .venv/bin/activate
fi

echo "📍 当前Python: $(which python3)"

# 检查Python依赖
echo ""
echo "🔍 检查Python依赖..."
MISSING_PYTHON_DEPS=false
for module in uvicorn fastapi sqlalchemy dashscope; do
    if ! python3 -c "import $module" 2>/dev/null; then
        echo "❌ 缺少依赖: $module"
        MISSING_PYTHON_DEPS=true
    fi
done

if [ "$MISSING_PYTHON_DEPS" = true ]; then
    echo ""
    echo "╔═══════════════════════════════════════════════════════╗"
    echo "║  ⚠️  请先安装Python依赖！                             ║"
    echo "╚═══════════════════════════════════════════════════════╝"
    echo ""
    echo "📝 安装步骤："
    echo ""
    echo "方式1：使用虚拟环境（推荐）"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
    echo "方式2：直接安装"
    echo "  pip3 install -r requirements.txt"
    echo ""
    echo "或者运行安装脚本："
    echo "  ./install.sh"
    echo ""
    exit 1
fi

echo "✅ Python依赖已安装"

# 检查前端依赖
echo ""
echo "🔍 检查前端依赖..."
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ 前端依赖未安装"
    echo ""
    echo "╔═══════════════════════════════════════════════════════╗"
    echo "║  ⚠️  请先安装前端依赖！                               ║"
    echo "╚═══════════════════════════════════════════════════════╝"
    echo ""
    echo "📝 安装步骤："
    echo "  cd frontend"
    echo "  npm install"
    echo "  cd .."
    echo ""
    echo "或者运行安装脚本："
    echo "  ./install.sh"
    echo ""
    exit 1
fi

echo "✅ 前端依赖已安装"

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
    echo "   1. 检查是否安装了所有依赖: pip3 install -r requirements.txt"
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
