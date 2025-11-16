"""
QwenImg Web UI - 全新设计版本 v4.0

特点：
    - 简洁高雅的现代化UI设计
    - 优化的代码结构，易于维护
    - 流畅的交互体验
    - 完善的错误处理
    - 异步任务管理

运行方式：
    streamlit run app.py
"""

import streamlit as st
import os
from pathlib import Path
from io import BytesIO
import sys
from datetime import datetime
import base64
import threading
from concurrent.futures import ThreadPoolExecutor
import time
from typing import Dict, Any, Optional, List
from PIL import Image

# 添加项目路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from qwenimg import QwenImg

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="QwenImg - 通义万相",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 样式定义 ====================
def apply_custom_styles():
    """应用自定义CSS样式 - 简洁高雅的设计"""
    st.markdown("""
    <style>
        /* 全局样式 */
        .main {
            background-color: #f8f9fa;
        }

        /* 标题样式 */
        .app-title {
            font-size: 2.5rem;
            font-weight: 600;
            color: #1a1a1a;
            text-align: center;
            margin-bottom: 0.5rem;
            letter-spacing: -0.5px;
        }

        .app-subtitle {
            text-align: center;
            color: #6c757d;
            font-size: 1rem;
            margin-bottom: 2rem;
            font-weight: 400;
        }

        /* 卡片样式 */
        .card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            margin-bottom: 1rem;
        }

        /* 按钮样式 */
        .stButton>button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s;
            border: none;
        }

        .stButton>button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        /* 主要按钮 */
        .stButton>button[kind="primary"] {
            background: #4f46e5;
            color: white;
        }

        /* 输入框样式 */
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea {
            border-radius: 8px;
            border: 1.5px solid #e5e7eb;
            transition: border-color 0.2s;
        }

        .stTextInput>div>div>input:focus,
        .stTextArea>div>div>textarea:focus {
            border-color: #4f46e5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }

        /* 选择框样式 */
        .stSelectbox>div>div>div {
            border-radius: 8px;
        }

        /* 进度条样式 */
        .stProgress>div>div>div {
            background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        }

        /* 成功消息 */
        .success-message {
            background: #d1fae5;
            color: #065f46;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #10b981;
            margin: 1rem 0;
        }

        /* 错误消息 */
        .error-message {
            background: #fee2e2;
            color: #991b1b;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #ef4444;
            margin: 1rem 0;
        }

        /* 信息消息 */
        .info-message {
            background: #dbeafe;
            color: #1e40af;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
            margin: 1rem 0;
        }

        /* 历史记录项 */
        .history-item {
            background: #f9fafb;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 0.75rem;
            border-left: 3px solid #4f46e5;
            transition: all 0.2s;
        }

        .history-item:hover {
            background: #f3f4f6;
            transform: translateX(2px);
        }

        .history-time {
            color: #9ca3af;
            font-size: 0.875rem;
            font-weight: 500;
        }

        .history-content {
            color: #374151;
            font-size: 0.9rem;
            margin-top: 0.25rem;
        }

        /* Tab样式 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 0.75rem 1.5rem;
            font-weight: 500;
        }

        /* 侧边栏样式 */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
        }

        /* 移除默认padding */
        .block-container {
            padding-top: 2rem;
        }

        /* 图片容器 */
        .image-container {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        /* 视频容器 */
        .video-container {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        /* 分隔线 */
        hr {
            margin: 2rem 0;
            border: none;
            border-top: 1px solid #e5e7eb;
        }

        /* 标签 */
        .tag {
            display: inline-block;
            background: #f3f4f6;
            color: #4b5563;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 500;
            margin-right: 0.5rem;
        }

        /* 隐藏streamlit默认元素 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==================== 工具函数 ====================

def init_session_state():
    """统一初始化session state"""
    # 全局状态
    defaults = {
        'history': [],
        'executor': ThreadPoolExecutor(max_workers=3),

        # 文生图
        't2i_results': None,
        't2i_task_status': 'idle',
        't2i_task_error': None,
        'prompt_t2i': "",
        'negative_prompt_t2i': "",
        'model_t2i': "wan2.5-t2i-preview",
        'size_t2i': "1024*1024",
        'n_images': 1,
        'seed_t2i': 0,
        'prompt_extend': True,
        'watermark_t2i': False,

        # 图生视频
        'i2v_result': None,
        'i2v_task_status': 'idle',
        'i2v_task_error': None,
        'uploaded_image': None,
        'prompt_i2v': "",
        'negative_prompt_i2v': "",
        'model_i2v': "wan2.5-i2v-preview",
        'resolution_i2v': "1080P",
        'duration_i2v': 10,
        'seed_i2v': 0,
        'watermark_i2v': False,

        # 文生视频
        't2v_result': None,
        't2v_task_status': 'idle',
        't2v_task_error': None,
        'prompt_t2v': "",
        'negative_prompt_t2v': "",
        'model_t2v': "wan2.5-t2v-preview",
        'resolution_t2v': "1080P",
        'duration_t2v': 10,
        'seed_t2v': 0,
        'watermark_t2v': False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def show_status_message(status: str, message: str, type: str = "info"):
    """显示状态消息"""
    icons = {"success": "✅", "error": "❌", "info": "ℹ️", "warning": "⚠️"}
    colors = {
        "success": ("#d1fae5", "#065f46", "#10b981"),
        "error": ("#fee2e2", "#991b1b", "#ef4444"),
        "info": ("#dbeafe", "#1e40af", "#3b82f6"),
        "warning": ("#fef3c7", "#92400e", "#f59e0b")
    }

    bg, text, border = colors.get(type, colors["info"])
    icon = icons.get(type, "ℹ️")

    st.markdown(f"""
    <div style="background: {bg}; color: {text}; padding: 1rem; border-radius: 8px;
                border-left: 4px solid {border}; margin: 1rem 0;">
        <strong>{icon} {status}</strong><br/>
        {message}
    </div>
    """, unsafe_allow_html=True)

# ==================== 异步任务函数 ====================

def run_t2i_task(client, kwargs):
    """执行文生图任务"""
    try:
        st.session_state.t2i_task_status = 'running'
        result = client.text_to_image(**kwargs)

        st.session_state.t2i_results = {
            'images': result if isinstance(result, list) else [result],
            'prompt': kwargs['prompt'],
            'params': kwargs
        }

        # 添加历史记录
        st.session_state.history.append({
            'type': '文生图',
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'prompt': kwargs['prompt'][:100],
            'count': kwargs['n'],
            'size': kwargs['size']
        })

        st.session_state.t2i_task_status = 'completed'

    except Exception as e:
        st.session_state.t2i_task_status = 'error'
        st.session_state.t2i_task_error = str(e)

def run_i2v_task(client, kwargs, temp_image_path):
    """执行图生视频任务"""
    try:
        st.session_state.i2v_task_status = 'running'
        video_url = client.image_to_video(**kwargs)

        st.session_state.i2v_result = {
            'url': video_url,
            'prompt': kwargs.get('prompt', ''),
            'params': kwargs
        }

        st.session_state.history.append({
            'type': '图生视频',
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'prompt': kwargs.get('prompt', '无')[:100],
            'resolution': kwargs['resolution'],
            'duration': kwargs['duration']
        })

        # 清理临时文件
        if temp_image_path and Path(temp_image_path).exists():
            Path(temp_image_path).unlink()

        st.session_state.i2v_task_status = 'completed'

    except Exception as e:
        st.session_state.i2v_task_status = 'error'
        st.session_state.i2v_task_error = str(e)

def run_t2v_task(client, kwargs):
    """执行文生视频任务"""
    try:
        st.session_state.t2v_task_status = 'running'
        video_url = client.text_to_video(**kwargs)

        st.session_state.t2v_result = {
            'url': video_url,
            'prompt': kwargs['prompt'],
            'params': kwargs
        }

        st.session_state.history.append({
            'type': '文生视频',
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'prompt': kwargs['prompt'][:100],
            'resolution': kwargs['resolution'],
            'duration': kwargs['duration']
        })

        st.session_state.t2v_task_status = 'completed'

    except Exception as e:
        st.session_state.t2v_task_status = 'error'
        st.session_state.t2v_task_error = str(e)

# ==================== 初始化 ====================

@st.cache_resource
def init_client(api_key: str, region: str):
    """初始化QwenImg客户端"""
    try:
        return QwenImg(api_key=api_key, region=region)
    except Exception as e:
        st.error(f"客户端初始化失败: {str(e)}")
        return None

# 初始化session state
init_session_state()

# 应用样式
apply_custom_styles()

# ==================== 页面标题 ====================

st.markdown('<div class="app-title">🎨 QwenImg</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">阿里云通义万相 - AI图片与视频生成</div>', unsafe_allow_html=True)

# ==================== 侧边栏 ====================

with st.sidebar:
    st.markdown("### ⚙️ 配置")

    api_key = st.text_input(
        "API Key",
        type="password",
        value=os.getenv("DASHSCOPE_API_KEY", ""),
        help="在阿里云百炼平台获取API Key",
        placeholder="sk-..."
    )

    region = st.selectbox(
        "服务地域",
        ["beijing", "singapore"],
        help="选择API服务地域"
    )

    if api_key:
        st.success("API Key 已配置")
    else:
        st.warning("请输入 API Key")

    st.markdown("---")

    # 历史记录
    st.markdown("### 📜 历史记录")

    if st.session_state.history:
        # 清空按钮
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**{len(st.session_state.history)} 条记录**")
        with col2:
            if st.button("清空", key="clear_history", use_container_width=True):
                st.session_state.history = []
                st.rerun()

        st.markdown("")

        # 显示最近10条
        for record in reversed(st.session_state.history[-10:]):
            type_emoji = {"文生图": "📝", "图生视频": "🎬", "文生视频": "🎥"}
            emoji = type_emoji.get(record['type'], "📝")

            with st.container():
                st.markdown(f"""
                <div class="history-item">
                    <div class="history-time">{emoji} {record['time']}</div>
                    <div class="history-content">{record.get('prompt', 'N/A')[:50]}...</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("暂无生成记录")

    st.markdown("---")

    # 帮助链接
    st.markdown("### 📚 帮助")
    st.markdown("""
    - [获取 API Key](https://help.aliyun.com/zh/model-studio/get-api-key)
    - [API 文档](https://help.aliyun.com/zh/model-studio/)
    - [GitHub 项目](https://github.com/cclank/qwenimg)
    """)

    st.markdown("---")
    st.markdown("**v4.0** | Powered by 岚叔")

# 初始化客户端
if api_key:
    client = init_client(api_key, region)
else:
    client = None

# ==================== 主界面 ====================

tab1, tab2, tab3 = st.tabs(["📝 文生图", "🎬 图生视频", "🎥 文生视频"])

# ==================== Tab 1: 文生图 ====================

with tab1:
    st.markdown("### 文字生成图片")
    st.markdown("使用文字描述生成高质量图片")
    st.markdown("")

    # 输入区域
    with st.container():
        prompt_t2i = st.text_area(
            "提示词 *",
            value=st.session_state.prompt_t2i,
            height=120,
            placeholder="例如: 一只可爱的橘猫坐在窗台上，阳光洒在它身上，背景是蓝天白云...",
            help="详细描述你想要生成的图片",
            key="prompt_t2i"
        )

        negative_prompt_t2i = st.text_input(
            "负面提示词（可选）",
            value=st.session_state.negative_prompt_t2i,
            placeholder="例如: 模糊、低质量、变形...",
            help="描述不希望出现的内容",
            key="negative_prompt_t2i"
        )

    # 参数设置
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        model_t2i = st.selectbox(
            "模型",
            ["wan2.5-t2i-preview", "wanx-v1"],
            index=["wan2.5-t2i-preview", "wanx-v1"].index(st.session_state.model_t2i),
            key="model_t2i"
        )

    with col2:
        size_t2i = st.selectbox(
            "尺寸",
            ["1024*1024", "1280*720", "720*1280"],
            index=["1024*1024", "1280*720", "720*1280"].index(st.session_state.size_t2i),
            key="size_t2i"
        )

    with col3:
        n_images = st.selectbox(
            "数量",
            [1, 2, 3, 4],
            index=[1, 2, 3, 4].index(st.session_state.n_images),
            key="n_images"
        )

    with col4:
        seed_t2i = st.number_input(
            "随机种子",
            min_value=0,
            value=st.session_state.seed_t2i,
            help="0表示随机",
            key="seed_t2i"
        )

    # 高级选项
    with st.expander("高级选项"):
        col1, col2 = st.columns(2)
        with col1:
            prompt_extend = st.checkbox(
                "自动扩展提示词",
                value=st.session_state.prompt_extend,
                key="prompt_extend",
                help="AI会自动优化和扩展你的提示词"
            )
        with col2:
            watermark_t2i = st.checkbox(
                "添加水印",
                value=st.session_state.watermark_t2i,
                key="watermark_t2i"
            )

    st.markdown("")

    # 操作按钮
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        generate_t2i = st.button(
            "🎨 生成图片",
            key="gen_t2i",
            type="primary",
            use_container_width=True,
            disabled=(st.session_state.t2i_task_status == 'running')
        )

    with col2:
        if st.session_state.t2i_results:
            if st.button("🗑️ 清除", key="clear_t2i", use_container_width=True):
                st.session_state.t2i_results = None
                st.session_state.t2i_task_status = 'idle'
                st.session_state.t2i_task_error = None
                st.rerun()

    with col3:
        if st.button("🔄 重置", key="reset_t2i", use_container_width=True):
            st.session_state.prompt_t2i = ""
            st.session_state.negative_prompt_t2i = ""
            st.rerun()

    # 任务状态显示
    if st.session_state.t2i_task_status == 'running':
        with st.spinner("正在生成图片，请稍候..."):
            st.progress(0.5, text="AI正在创作中...")
        st.info("💡 您可以切换到其他标签页继续操作，任务会在后台执行")
        # 自动刷新检查任务状态
        time.sleep(0.5)
        st.rerun()

    elif st.session_state.t2i_task_status == 'error':
        show_status_message("生成失败", st.session_state.t2i_task_error, "error")
        if st.button("重试", key="retry_t2i"):
            st.session_state.t2i_task_status = 'idle'
            st.session_state.t2i_task_error = None
            st.rerun()

    elif st.session_state.t2i_task_status == 'completed' and st.session_state.t2i_results:
        show_status_message(
            "生成成功",
            f"已成功生成 {len(st.session_state.t2i_results['images'])} 张图片",
            "success"
        )
        st.session_state.t2i_task_status = 'idle'

    # 生成操作
    if generate_t2i:
        if not client:
            show_status_message("配置错误", "请先在侧边栏配置 API Key", "error")
        elif not st.session_state.prompt_t2i.strip():
            show_status_message("输入错误", "请输入提示词", "warning")
        else:
            kwargs = {
                "prompt": st.session_state.prompt_t2i,
                "model": st.session_state.model_t2i,
                "size": st.session_state.size_t2i,
                "n": st.session_state.n_images,
                "prompt_extend": st.session_state.prompt_extend,
                "watermark": st.session_state.watermark_t2i,
                "negative_prompt": st.session_state.negative_prompt_t2i,
                "save": False,
            }

            if st.session_state.seed_t2i > 0:
                kwargs["seed"] = st.session_state.seed_t2i

            st.session_state.t2i_task_status = 'running'
            st.session_state.t2i_task_error = None
            st.session_state.executor.submit(run_t2i_task, client, kwargs)
            st.rerun()

    # 显示结果
    if st.session_state.t2i_results:
        st.markdown("---")
        st.markdown("### 📸 生成结果")

        images = st.session_state.t2i_results['images']

        if len(images) == 1:
            st.image(images[0], use_container_width=True)
            buf = BytesIO()
            images[0].save(buf, format="PNG")
            st.download_button(
                "📥 下载图片",
                data=buf.getvalue(),
                file_name=f"qwenimg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                mime="image/png",
                use_container_width=True
            )
        else:
            cols = st.columns(2)
            for i, img in enumerate(images):
                with cols[i % 2]:
                    st.image(img, use_container_width=True)
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button(
                        f"📥 下载图片 {i+1}",
                        data=buf.getvalue(),
                        file_name=f"qwenimg_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        mime="image/png",
                        key=f"dl_t2i_{i}",
                        use_container_width=True
                    )

# ==================== Tab 2: 图生视频 ====================

with tab2:
    st.markdown("### 图片生成视频")
    st.markdown("上传图片，生成动态视频")
    st.markdown("")

    # 图片上传
    uploaded_file = st.file_uploader(
        "上传图片 *",
        type=["png", "jpg", "jpeg"],
        help="支持 PNG、JPG、JPEG 格式",
        key="image_uploader"
    )

    if uploaded_file is not None:
        st.session_state.uploaded_image = uploaded_file

    if st.session_state.uploaded_image:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(st.session_state.uploaded_image, caption="预览", use_container_width=True)

    # 提示词
    prompt_i2v = st.text_area(
        "提示词（可选）",
        value=st.session_state.prompt_i2v,
        height=100,
        placeholder="例如: 画面中的人物缓缓转身，云雾翻涌，镜头缓慢推进...",
        help="描述视频中的动作和变化",
        key="prompt_i2v"
    )

    negative_prompt_i2v = st.text_input(
        "负面提示词（可选）",
        value=st.session_state.negative_prompt_i2v,
        placeholder="例如: 模糊、抖动、失真...",
        key="negative_prompt_i2v"
    )

    # 参数设置
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        model_i2v = st.selectbox(
            "模型",
            ["wan2.5-i2v-preview"],
            key="model_i2v"
        )

    with col2:
        resolution_i2v = st.selectbox(
            "分辨率",
            ["1080P", "720P", "480P"],
            index=["1080P", "720P", "480P"].index(st.session_state.resolution_i2v),
            key="resolution_i2v"
        )

    with col3:
        duration_i2v = st.selectbox(
            "时长(秒)",
            [10, 5],
            index=[10, 5].index(st.session_state.duration_i2v),
            key="duration_i2v"
        )

    with col4:
        seed_i2v = st.number_input(
            "随机种子",
            min_value=0,
            value=st.session_state.seed_i2v,
            key="seed_i2v"
        )

    with st.expander("高级选项"):
        watermark_i2v = st.checkbox(
            "添加水印",
            value=st.session_state.watermark_i2v,
            key="watermark_i2v"
        )

    st.markdown("")

    # 操作按钮
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        generate_i2v = st.button(
            "🎬 生成视频",
            key="gen_i2v",
            type="primary",
            use_container_width=True,
            disabled=(st.session_state.i2v_task_status == 'running')
        )

    with col2:
        if st.session_state.i2v_result:
            if st.button("🗑️ 清除", key="clear_i2v", use_container_width=True):
                st.session_state.i2v_result = None
                st.session_state.i2v_task_status = 'idle'
                st.session_state.i2v_task_error = None
                st.rerun()

    with col3:
        if st.button("🔄 重置", key="reset_i2v", use_container_width=True):
            st.session_state.prompt_i2v = ""
            st.session_state.negative_prompt_i2v = ""
            st.session_state.uploaded_image = None
            st.rerun()

    # 任务状态
    if st.session_state.i2v_task_status == 'running':
        estimated = st.session_state.duration_i2v * 10
        with st.spinner(f"正在生成视频，预计需要 {estimated}-{estimated+30} 秒..."):
            st.progress(0.5, text="AI正在创作中...")
        st.info("💡 您可以切换到其他标签页继续操作，任务会在后台执行")
        time.sleep(0.5)
        st.rerun()

    elif st.session_state.i2v_task_status == 'error':
        show_status_message("生成失败", st.session_state.i2v_task_error, "error")
        if st.button("重试", key="retry_i2v"):
            st.session_state.i2v_task_status = 'idle'
            st.session_state.i2v_task_error = None
            st.rerun()

    elif st.session_state.i2v_task_status == 'completed' and st.session_state.i2v_result:
        show_status_message("生成成功", "视频已生成完成", "success")
        st.session_state.i2v_task_status = 'idle'

    # 生成操作
    if generate_i2v:
        if not client:
            show_status_message("配置错误", "请先在侧边栏配置 API Key", "error")
        elif not st.session_state.uploaded_image:
            show_status_message("输入错误", "请上传图片", "warning")
        else:
            try:
                temp_image_path = Path("/tmp/qwenimg_upload_i2v.png")
                with open(temp_image_path, "wb") as f:
                    f.write(st.session_state.uploaded_image.getbuffer())

                kwargs = {
                    "image": str(temp_image_path),
                    "model": st.session_state.model_i2v,
                    "resolution": st.session_state.resolution_i2v,
                    "duration": st.session_state.duration_i2v,
                    "watermark": st.session_state.watermark_i2v,
                    "prompt": st.session_state.prompt_i2v,
                    "negative_prompt": st.session_state.negative_prompt_i2v,
                }

                if st.session_state.seed_i2v > 0:
                    kwargs["seed"] = st.session_state.seed_i2v

                st.session_state.i2v_task_status = 'running'
                st.session_state.i2v_task_error = None
                st.session_state.executor.submit(run_i2v_task, client, kwargs, str(temp_image_path))
                st.rerun()

            except Exception as e:
                show_status_message("准备失败", str(e), "error")

    # 显示结果
    if st.session_state.i2v_result:
        st.markdown("---")
        st.markdown("### 🎬 生成结果")

        video_url = st.session_state.i2v_result['url']
        st.video(video_url)
        st.markdown(f"**视频链接**: [{video_url}]({video_url})")
        st.info("💡 点击链接在新标签页打开，右键可保存视频")

# ==================== Tab 3: 文生视频 ====================

with tab3:
    st.markdown("### 文字生成视频")
    st.markdown("使用文字描述生成动态视频")
    st.markdown("")

    # 提示词
    prompt_t2v = st.text_area(
        "提示词 *",
        value=st.session_state.prompt_t2v,
        height=120,
        placeholder="例如: 一只柴犬在绿色草地上奔跑，阳光明媚，春天的气息，镜头跟随...",
        help="详细描述视频场景和动作",
        key="prompt_t2v"
    )

    negative_prompt_t2v = st.text_input(
        "负面提示词（可选）",
        value=st.session_state.negative_prompt_t2v,
        placeholder="例如: 模糊、静止、低质量...",
        key="negative_prompt_t2v"
    )

    # 参数设置
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        model_t2v = st.selectbox(
            "模型",
            ["wan2.5-t2v-preview"],
            key="model_t2v"
        )

    with col2:
        resolution_t2v = st.selectbox(
            "分辨率",
            ["1080P", "720P", "480P"],
            index=["1080P", "720P", "480P"].index(st.session_state.resolution_t2v),
            key="resolution_t2v"
        )

    with col3:
        duration_t2v = st.selectbox(
            "时长(秒)",
            [10, 5],
            index=[10, 5].index(st.session_state.duration_t2v),
            key="duration_t2v"
        )

    with col4:
        seed_t2v = st.number_input(
            "随机种子",
            min_value=0,
            value=st.session_state.seed_t2v,
            key="seed_t2v"
        )

    with st.expander("高级选项"):
        watermark_t2v = st.checkbox(
            "添加水印",
            value=st.session_state.watermark_t2v,
            key="watermark_t2v"
        )

    st.markdown("")

    # 操作按钮
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        generate_t2v = st.button(
            "🎥 生成视频",
            key="gen_t2v",
            type="primary",
            use_container_width=True,
            disabled=(st.session_state.t2v_task_status == 'running')
        )

    with col2:
        if st.session_state.t2v_result:
            if st.button("🗑️ 清除", key="clear_t2v", use_container_width=True):
                st.session_state.t2v_result = None
                st.session_state.t2v_task_status = 'idle'
                st.session_state.t2v_task_error = None
                st.rerun()

    with col3:
        if st.button("🔄 重置", key="reset_t2v", use_container_width=True):
            st.session_state.prompt_t2v = ""
            st.session_state.negative_prompt_t2v = ""
            st.rerun()

    # 任务状态
    if st.session_state.t2v_task_status == 'running':
        estimated = st.session_state.duration_t2v * 10
        with st.spinner(f"正在生成视频，预计需要 {estimated}-{estimated+30} 秒..."):
            st.progress(0.5, text="AI正在创作中...")
        st.info("💡 您可以切换到其他标签页继续操作，任务会在后台执行")
        time.sleep(0.5)
        st.rerun()

    elif st.session_state.t2v_task_status == 'error':
        show_status_message("生成失败", st.session_state.t2v_task_error, "error")
        if st.button("重试", key="retry_t2v"):
            st.session_state.t2v_task_status = 'idle'
            st.session_state.t2v_task_error = None
            st.rerun()

    elif st.session_state.t2v_task_status == 'completed' and st.session_state.t2v_result:
        show_status_message("生成成功", "视频已生成完成", "success")
        st.session_state.t2v_task_status = 'idle'

    # 生成操作
    if generate_t2v:
        if not client:
            show_status_message("配置错误", "请先在侧边栏配置 API Key", "error")
        elif not st.session_state.prompt_t2v.strip():
            show_status_message("输入错误", "请输入提示词", "warning")
        else:
            kwargs = {
                "prompt": st.session_state.prompt_t2v,
                "model": st.session_state.model_t2v,
                "resolution": st.session_state.resolution_t2v,
                "duration": st.session_state.duration_t2v,
                "watermark": st.session_state.watermark_t2v,
                "negative_prompt": st.session_state.negative_prompt_t2v,
            }

            if st.session_state.seed_t2v > 0:
                kwargs["seed"] = st.session_state.seed_t2v

            st.session_state.t2v_task_status = 'running'
            st.session_state.t2v_task_error = None
            st.session_state.executor.submit(run_t2v_task, client, kwargs)
            st.rerun()

    # 显示结果
    if st.session_state.t2v_result:
        st.markdown("---")
        st.markdown("### 🎥 生成结果")

        video_url = st.session_state.t2v_result['url']
        st.video(video_url)
        st.markdown(f"**视频链接**: [{video_url}]({video_url})")
        st.info("💡 点击链接在新标签页打开，右键可保存视频")

# ==================== 页脚 ====================

st.markdown("---")

with st.expander("💡 使用技巧", expanded=False):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **文生图技巧**
        - 详细描述场景、主体、风格
        - 使用专业术语提升质量
        - 固定种子可重现结果
        - 尝试不同尺寸和模型
        """)

    with col2:
        st.markdown("""
        **图生视频技巧**
        - 上传清晰、构图好的图片
        - 描述具体的动作和变化
        - 使用镜头语言增强效果
        - 合理设置分辨率和时长
        """)

    with col3:
        st.markdown("""
        **文生视频技巧**
        - 清晰描述场景和主体
        - 指定镜头运动方式
        - 使用"电影级"等关键词
        - 注意时长与内容匹配
        """)

st.markdown("""
<div style="text-align: center; color: #6c757d; padding: 1rem;">
    <p><strong>QwenImg v4.0</strong> - 简洁、高雅、流畅</p>
    <p>Made with ❤️ by 岚叔 | <a href="https://github.com/cclank/qwenimg" target="_blank">GitHub</a></p>
</div>
""", unsafe_allow_html=True)
