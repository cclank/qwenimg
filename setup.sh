#!/bin/bash

echo "🔧 QwenImg 环境设置"
echo ""

# 1. 清理旧环境
echo "1️⃣ 清理旧的虚拟环境..."
rm -rf venv .venv

# 2. 创建新的虚拟环境
echo "2️⃣ 创建虚拟环境..."
python3 -m venv venv

# 3. 激活虚拟环境
echo "3️⃣ 激活虚拟环境..."
source venv/bin/activate

# 4. 升级 pip
echo "4️⃣ 升级 pip..."
pip install --upgrade pip

# 5. 安装 Python 依赖
echo "5️⃣ 安装 Python 依赖..."
pip install -r requirements.txt

# 6. 验证安装
echo ""
echo "6️⃣ 验证安装..."
python3 -c "import uvicorn, fastapi, sqlalchemy, dashscope; print('✅ Python 依赖安装成功')"

# 7. 安装前端依赖
echo ""
echo "7️⃣ 安装前端依赖..."
cd frontend
npm install
cd ..

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║              ✅ 环境设置完成！                        ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
echo "下一步："
echo "1. 配置 API Key: export DASHSCOPE_API_KEY=\"your-key\""
echo "2. 启动服务: ./start_dev.sh"
echo ""
