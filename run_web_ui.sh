#!/bin/bash

# QwenImg Web UI 启动脚本
# Author: 岚叔

echo "🎨 QwenImg Web UI 启动器"
echo "========================================"
echo ""

# 检查是否安装了 streamlit
if ! command -v streamlit &> /dev/null; then
    echo "❌ 未检测到 Streamlit，正在安装..."
    pip install streamlit
    echo ""
fi

# 检查 API Key
if [ -z "$DASHSCOPE_API_KEY" ]; then
    echo "⚠️  提示：未检测到环境变量 DASHSCOPE_API_KEY"
    echo "   你可以在 Web 界面中手动输入 API Key"
    echo ""
fi

echo "✅ 启动 Web 界面..."
echo "   访问地址: http://localhost:8501"
echo ""
echo "   按 Ctrl+C 停止服务"
echo ""
echo "========================================"
echo ""

# 启动 Streamlit
streamlit run app.py
