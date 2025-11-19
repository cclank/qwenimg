#!/bin/bash

# QwenImg 一键安装配置脚本
# 适用于全新环境的快速部署

set -e  # 遇到错误立即退出

echo "╔═══════════════════════════════════════════════════════╗"
echo "║     QwenImg AI 创作平台 - 一键安装配置                ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否在项目根目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}❌ 错误：请在项目根目录运行此脚本${NC}"
    exit 1
fi

echo "📍 当前目录: $(pwd)"
echo ""

# ============================================
# 1. 检查系统依赖
# ============================================
echo "🔍 步骤 1/6: 检查系统依赖..."
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 未找到 Python 3${NC}"
    echo "请先安装 Python 3.8+: https://www.python.org/downloads/"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ 未找到 Node.js${NC}"
    echo "请先安装 Node.js 16+: https://nodejs.org/"
    exit 1
fi
NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)
echo -e "${GREEN}✅ Node.js $NODE_VERSION${NC}"
echo -e "${GREEN}✅ npm $NPM_VERSION${NC}"

echo ""

# ============================================
# 2. 创建虚拟环境
# ============================================
echo "🐍 步骤 2/6: 配置 Python 虚拟环境..."
echo ""

# 清理旧环境
if [ -d "venv" ]; then
    echo "🗑️  清理旧的虚拟环境..."
    rm -rf venv
fi

# 创建新环境
echo "📦 创建虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
echo "🔌 激活虚拟环境..."
source venv/bin/activate

# 升级 pip
echo "⬆️  升级 pip..."
pip install --upgrade pip -q

echo -e "${GREEN}✅ 虚拟环境配置完成${NC}"
echo ""

# ============================================
# 3. 安装 Python 依赖
# ============================================
echo "📦 步骤 3/6: 安装 Python 依赖..."
echo ""

if ! pip install -r requirements.txt; then
    echo -e "${RED}❌ Python 依赖安装失败${NC}"
    echo ""
    echo "💡 建议："
    echo "   1. 检查网络连接"
    echo "   2. 尝试使用国内镜像源："
    echo "      pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple"
    exit 1
fi

echo -e "${GREEN}✅ Python 依赖安装成功${NC}"
echo ""

# ============================================
# 4. 安装前端依赖
# ============================================
echo "📦 步骤 4/6: 安装前端依赖..."
echo ""

cd frontend

if ! npm install; then
    echo -e "${RED}❌ 前端依赖安装失败${NC}"
    echo ""
    echo "💡 建议："
    echo "   1. 清理缓存重试："
    echo "      npm cache clean --force"
    echo "      rm -rf node_modules package-lock.json"
    echo "      npm install"
    echo ""
    echo "   2. 或使用淘宝镜像："
    echo "      npm install --registry=https://registry.npmmirror.com"
    cd ..
    exit 1
fi

cd ..
echo -e "${GREEN}✅ 前端依赖安装成功${NC}"
echo ""

# ============================================
# 5. 配置环境变量
# ============================================
echo "🔑 步骤 5/6: 配置环境变量..."
echo ""

# 检查根目录 .env 文件
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 从 .env.example 创建 .env 文件..."
        cp .env.example .env
        echo -e "${YELLOW}⚠️  请编辑根目录的 .env 文件，填入你的 API Key${NC}"
    else
        echo "📝 创建 .env 文件..."
        echo "DASHSCOPE_API_KEY=your_api_key_here" > .env
        echo -e "${YELLOW}⚠️  请编辑根目录的 .env 文件，填入你的 API Key${NC}"
    fi
else
    echo -e "${GREEN}✅ .env 文件已存在${NC}"
fi

# 检查后端 .env 文件
if [ ! -f "backend/.env" ]; then
    if [ -f "backend/.env.example" ]; then
        echo "📝 从 backend/.env.example 创建 backend/.env 文件..."
        cp backend/.env.example backend/.env
    fi
fi

echo ""

# ============================================
# 6. 验证安装
# ============================================
echo "✅ 步骤 6/6: 验证安装..."
echo ""

# 验证 Python 包
if python3 -c "import uvicorn, fastapi, sqlalchemy, dashscope" 2>/dev/null; then
    echo -e "${GREEN}✅ Python 依赖验证成功${NC}"
else
    echo -e "${YELLOW}⚠️  Python 依赖验证失败，但可能不影响使用${NC}"
fi

# 验证前端依赖
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✅ 前端依赖验证成功${NC}"
else
    echo -e "${YELLOW}⚠️  前端依赖验证失败${NC}"
fi

echo ""

# ============================================
# 7. 恢复示例数据（如果存在）
# ============================================
if [ -d "demo_data_backup" ] && [ -f "demo_data_backup/restore.sh" ]; then
    echo "🎨 步骤 7/7: 恢复示例数据..."
    echo ""
    
    cd demo_data_backup
    if ./restore.sh 2>/dev/null; then
        echo -e "${GREEN}✅ 示例数据恢复成功${NC}"
    else
        echo -e "${YELLOW}⚠️  示例数据恢复失败（不影响使用）${NC}"
    fi
    cd ..
    echo ""
fi

# ============================================
# 完成提示
# ============================================
echo "╔═══════════════════════════════════════════════════════╗"
echo "║              ✅ 安装配置完成！                        ║"
echo "╠═══════════════════════════════════════════════════════╣"
echo "║  下一步操作：                                         ║"
echo "║                                                       ║"
echo "║  1️⃣  配置 API Key（必须）                             ║"
echo "║     编辑项目根目录的 .env 文件：                       ║"
echo "║     nano .env                                        ║"
echo "║                                                       ║"
echo "║     或设置环境变量：                                   ║"
echo "║     export DASHSCOPE_API_KEY=\"your_key_here\"         ║"
echo "║                                                       ║"
echo "║  2️⃣  启动服务                                         ║"
echo "║     ./run.sh                                         ║"
echo "║                                                       ║"
echo "║  3️⃣  访问应用                                         ║"
echo "║     前端: http://localhost:5173                      ║"
echo "║     后端: http://localhost:8000                      ║"
echo "║                                                       ║"
echo "║  📖 获取 API Key：                                    ║"
echo "║     https://dashscope.console.aliyun.com/apiKey      ║"
echo "║                                                       ║"
echo "║  📚 查看文档：                                        ║"
echo "║     cat README.md                                    ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
