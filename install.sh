#!/bin/bash

# QwenImg 安装脚本 - 仅安装依赖，不启动服务

echo "╔═══════════════════════════════════════════════════════╗"
echo "║     QwenImg AI 创作平台 - 依赖安装                    ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# 检查是否在项目根目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3"
    echo "   请先安装Python 3.8+: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python版本: $(python3 --version)"

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误：未找到Node.js"
    echo "   请先安装Node.js 16+: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js版本: $(node --version)"
echo "✅ npm版本: $(npm --version)"
echo ""

# 安装Python依赖
echo "📦 安装Python依赖（从根目录）..."

if ! pip3 install -r requirements.txt; then
    echo ""
    echo "❌ Python依赖安装失败"
    echo ""
    echo "💡 建议："
    echo "   1. 使用虚拟环境（推荐）："
    echo "      python3 -m venv venv"
    echo "      source venv/bin/activate  # Windows: venv\\Scripts\\activate"
    echo "      pip install -r requirements.txt"
    echo ""
    echo "   2. 或升级pip："
    echo "      pip3 install --upgrade pip"
    echo "      pip3 install -r requirements.txt"
    exit 1
fi

echo "✅ Python依赖安装成功"
echo ""

# 安装前端依赖
echo "📦 安装前端npm依赖..."
cd frontend

if ! npm install; then
    echo ""
    echo "❌ 前端依赖安装失败"
    echo ""
    echo "💡 建议："
    echo "   1. 清理缓存重试："
    echo "      npm cache clean --force"
    echo "      rm -rf node_modules package-lock.json"
    echo "      npm install"
    echo ""
    echo "   2. 或使用yarn："
    echo "      npm install -g yarn"
    echo "      yarn install"
    exit 1
fi

cd ..
echo "✅ 前端依赖安装成功"
echo ""

# 配置环境变量
echo "🔑 配置API Key..."
if [ ! -f ".env" ]; then
    echo "📝 创建根目录 .env 文件..."
    cp .env.example .env
    echo ""
    echo "⚠️  请编辑 .env 文件，填入你的API Key："
    echo "   nano .env  # 或使用其他编辑器"
    echo ""
    echo "   或者设置环境变量（推荐）："
    echo "   export DASHSCOPE_API_KEY=\"your_api_key_here\""
else
    echo "✅ .env 文件已存在"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║              ✅ 安装完成！                            ║"
echo "╠═══════════════════════════════════════════════════════╣"
echo "║  下一步：                                             ║"
echo "║                                                       ║"
echo "║  1. 配置API Key（二选一）：                           ║"
echo "║     export DASHSCOPE_API_KEY=\"your_key\"              ║"
echo "║     或编辑 backend/.env 文件                          ║"
echo "║                                                       ║"
echo "║  2. 启动服务：                                        ║"
echo "║     ./start_dev.sh                                   ║"
echo "║                                                       ║"
echo "║  获取API Key：                                        ║"
echo "║  https://dashscope.console.aliyun.com/apiKey         ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
