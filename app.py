"""
QwenImg Web UI - 基于 Streamlit 的 Web 界面（改进版）

运行方式：
    streamlit run app.py

改进内容：
    - 使用 session_state 保存结果，切换 tab 不会丢失
    - 添加历史记录功能
    - 改进用户体验
"""

import streamlit as st
import os
from pathlib import Path
from io import BytesIO
import sys
from datetime import datetime
import base64

# 添加项目路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from qwenimg import QwenImg

# 页面配置
st.set_page_config(
    page_title="QwenImg - 通义万相图片视频生成",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化 session_state
if 'history' not in st.session_state:
    st.session_state.history = []

if 't2i_results' not in st.session_state:
    st.session_state.t2i_results = None

if 'i2v_result' not in st.session_state:
    st.session_state.i2v_result = None

if 't2v_result' not in st.session_state:
    st.session_state.t2v_result = None

if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None

# 自定义 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
        margin: 1rem 0;
    }
    .history-item {
        padding: 0.8rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
        border-left: 3px solid #667eea;
        border-radius: 3px;
    }
    .time-badge {
        color: #888;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<div class="main-header">🎨 QwenImg</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">阿里云百炼通义万相 - 图片与视频生成</div>', unsafe_allow_html=True)

# 侧边栏 - API Key 配置
with st.sidebar:
    st.header("⚙️ 配置")

    api_key = st.text_input(
        "DashScope API Key",
        type="password",
        value=os.getenv("DASHSCOPE_API_KEY", ""),
        help="获取 API Key: https://help.aliyun.com/zh/model-studio/get-api-key"
    )

    region = st.selectbox(
        "地域选择",
        ["beijing", "singapore"],
        help="不同地域需要使用对应地域的 API Key"
    )

    st.markdown("---")

    # 历史记录
    st.header("📜 历史记录")

    if st.session_state.history:
        if st.button("🗑️ 清空历史", key="clear_history"):
            st.session_state.history = []
            st.rerun()

        st.markdown(f"**共 {len(st.session_state.history)} 条记录**")

        # 显示最近 5 条
        for i, record in enumerate(reversed(st.session_state.history[-5:])):
            with st.expander(f"{record['type']} - {record['time']}", expanded=False):
                st.markdown(f"**提示词**: {record.get('prompt', 'N/A')[:50]}...")
                if record['type'] == '文生图':
                    st.markdown(f"**数量**: {record.get('count', 1)} 张")
                elif record['type'] in ['图生视频', '文生视频']:
                    st.markdown(f"**分辨率**: {record.get('resolution', 'N/A')}")
                    st.markdown(f"**时长**: {record.get('duration', 'N/A')} 秒")
    else:
        st.info("暂无历史记录")

    st.markdown("---")

    st.header("📚 文档")
    st.markdown("""
    - [获取 API Key](https://help.aliyun.com/zh/model-studio/get-api-key)
    - [文生图文档](https://help.aliyun.com/zh/model-studio/text-to-image-v2-api-reference)
    - [图生视频文档](https://help.aliyun.com/zh/model-studio/image-to-video-api-reference)
    """)

    st.markdown("---")
    st.markdown("**Powered by 岚叔**")
    st.markdown("GitHub: [cclank/qwenimg](https://github.com/cclank/qwenimg)")

# 初始化客户端
@st.cache_resource
def init_client(api_key, region):
    try:
        return QwenImg(api_key=api_key, region=region)
    except Exception as e:
        st.error(f"初始化失败: {str(e)}")
        return None

if api_key:
    client = init_client(api_key, region)
else:
    st.warning("⚠️ 请在侧边栏输入 API Key")
    client = None

# 主界面 - 功能选择
tab1, tab2, tab3 = st.tabs(["📝 文生图", "🎬 图生视频", "🎥 文生视频"])

# ==================== 文生图 ====================
with tab1:
    st.header("文生图 (Text-to-Image)")

    col1, col2 = st.columns([2, 1])

    with col1:
        prompt_t2i = st.text_area(
            "提示词",
            height=150,
            placeholder="描述你想要生成的图片，例如：一只可爱的橘猫坐在窗台上...",
            help="详细描述你想要生成的图片内容",
            key="prompt_t2i_input"
        )

        negative_prompt_t2i = st.text_input(
            "负面提示词",
            placeholder="模糊、粗糙、色彩暗淡...",
            help="描述你不想在图片中出现的内容",
            key="negative_t2i_input"
        )

    with col2:
        model_t2i = st.selectbox(
            "模型",
            ["wan2.5-t2i-preview", "wanx-v1"],
            help="选择文生图模型",
            key="model_t2i_select"
        )

        size_t2i = st.selectbox(
            "尺寸",
            ["1024*1024", "1280*720", "720*1280"],
            help="选择图片尺寸",
            key="size_t2i_select"
        )

        n_images = st.slider(
            "生成数量",
            min_value=1,
            max_value=4,
            value=1,
            help="一次生成的图片数量（1-4）",
            key="n_images_slider"
        )

        seed_t2i = st.number_input(
            "随机种子（可选）",
            min_value=0,
            value=0,
            help="固定种子可重现结果，0 表示随机",
            key="seed_t2i_input"
        )

        prompt_extend = st.checkbox("自动扩展提示词", value=True, key="prompt_extend_check")
        watermark_t2i = st.checkbox("添加水印", value=False, key="watermark_t2i_check")

    col_btn1, col_btn2 = st.columns([3, 1])

    with col_btn1:
        generate_t2i = st.button("🎨 生成图片", key="t2i_button", use_container_width=True)

    with col_btn2:
        if st.session_state.t2i_results:
            if st.button("🗑️ 清除结果", key="clear_t2i", use_container_width=True):
                st.session_state.t2i_results = None
                st.rerun()

    if generate_t2i:
        if not client:
            st.error("请先配置 API Key")
        elif not prompt_t2i:
            st.warning("请输入提示词")
        else:
            with st.spinner("正在生成图片，请稍候..."):
                try:
                    kwargs = {
                        "prompt": prompt_t2i,
                        "model": model_t2i,
                        "size": size_t2i,
                        "n": n_images,
                        "prompt_extend": prompt_extend,
                        "watermark": watermark_t2i,
                        "negative_prompt": negative_prompt_t2i,
                        "save": False,
                    }

                    if seed_t2i > 0:
                        kwargs["seed"] = seed_t2i

                    result = client.text_to_image(**kwargs)

                    # 保存到 session_state
                    st.session_state.t2i_results = {
                        'images': result if isinstance(result, list) else [result],
                        'prompt': prompt_t2i,
                        'params': kwargs
                    }

                    # 添加到历史记录
                    st.session_state.history.append({
                        'type': '文生图',
                        'time': datetime.now().strftime("%H:%M:%S"),
                        'prompt': prompt_t2i,
                        'count': n_images,
                        'size': size_t2i
                    })

                    st.success(f"✅ 成功生成 {n_images} 张图片！")
                    st.rerun()

                except Exception as e:
                    st.error(f"生成失败: {str(e)}")

    # 显示结果（从 session_state 读取）
    if st.session_state.t2i_results:
        st.markdown("---")
        st.subheader("📸 生成结果")

        images = st.session_state.t2i_results['images']
        n = len(images)

        if n == 1:
            st.image(images[0], caption="生成的图片", use_container_width=True)

            buf = BytesIO()
            images[0].save(buf, format="PNG")
            st.download_button(
                label="📥 下载图片",
                data=buf.getvalue(),
                file_name=f"qwenimg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                mime="image/png",
                key="download_t2i_single"
            )
        else:
            cols = st.columns(min(n, 2))
            for i, img in enumerate(images):
                with cols[i % 2]:
                    st.image(img, caption=f"图片 {i+1}", use_container_width=True)

                    buf = BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button(
                        label=f"📥 下载图片 {i+1}",
                        data=buf.getvalue(),
                        file_name=f"qwenimg_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        mime="image/png",
                        key=f"download_t2i_{i}"
                    )

# ==================== 图生视频 ====================
with tab2:
    st.header("图生视频 (Image-to-Video)")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "上传图片",
            type=["png", "jpg", "jpeg"],
            help="上传要生成视频的图片",
            key="image_uploader"
        )

        # 保存上传的文件到 session_state
        if uploaded_file is not None:
            st.session_state.uploaded_image = uploaded_file

        if st.session_state.uploaded_image:
            st.image(st.session_state.uploaded_image, caption="上传的图片", use_container_width=True)

        prompt_i2v = st.text_area(
            "提示词（可选）",
            height=120,
            placeholder="描述视频中的动作和变化，例如：角色缓缓转身，云雾翻涌...",
            help="描述视频的动态内容",
            key="prompt_i2v_input"
        )

        negative_prompt_i2v = st.text_input(
            "负面提示词",
            placeholder="模糊、抖动、失真...",
            help="描述不希望出现的内容",
            key="negative_i2v_input"
        )

    with col2:
        model_i2v = st.selectbox(
            "模型",
            ["wan2.5-i2v-preview"],
            help="选择图生视频模型",
            key="model_i2v_select"
        )

        resolution_i2v = st.selectbox(
            "分辨率",
            ["1080P", "720P", "480P"],
            help="选择视频分辨率",
            key="resolution_i2v_select"
        )

        duration_i2v = st.selectbox(
            "时长（秒）",
            [10, 5],
            help="选择视频时长",
            key="duration_i2v_select"
        )

        seed_i2v = st.number_input(
            "随机种子（可选）",
            min_value=0,
            value=0,
            help="固定种子可重现结果，0 表示随机",
            key="seed_i2v_input"
        )

        watermark_i2v = st.checkbox("添加水印", value=False, key="watermark_i2v_check")

    col_btn1, col_btn2 = st.columns([3, 1])

    with col_btn1:
        generate_i2v = st.button("🎬 生成视频", key="i2v_button", use_container_width=True)

    with col_btn2:
        if st.session_state.i2v_result:
            if st.button("🗑️ 清除结果", key="clear_i2v", use_container_width=True):
                st.session_state.i2v_result = None
                st.rerun()

    if generate_i2v:
        if not client:
            st.error("请先配置 API Key")
        elif not st.session_state.uploaded_image:
            st.warning("请上传图片")
        else:
            # 显示预估时间
            estimated_time = duration_i2v * 10  # 粗略估计
            st.info(f"⏱️ 预计需要 {estimated_time}-{estimated_time+30} 秒，请耐心等待...")

            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # 保存上传的图片到临时文件
                temp_image_path = Path("/tmp/qwenimg_upload.png")
                with open(temp_image_path, "wb") as f:
                    f.write(st.session_state.uploaded_image.getbuffer())

                progress_bar.progress(10)
                status_text.text("正在准备图片...")

                kwargs = {
                    "image": str(temp_image_path),
                    "model": model_i2v,
                    "resolution": resolution_i2v,
                    "duration": duration_i2v,
                    "watermark": watermark_i2v,
                    "prompt": prompt_i2v,
                    "negative_prompt": negative_prompt_i2v,
                }

                if seed_i2v > 0:
                    kwargs["seed"] = seed_i2v

                progress_bar.progress(20)
                status_text.text("正在生成视频...")

                video_url = client.image_to_video(**kwargs)

                progress_bar.progress(100)
                status_text.text("生成完成！")

                # 保存到 session_state
                st.session_state.i2v_result = {
                    'url': video_url,
                    'prompt': prompt_i2v,
                    'params': kwargs
                }

                # 添加到历史记录
                st.session_state.history.append({
                    'type': '图生视频',
                    'time': datetime.now().strftime("%H:%M:%S"),
                    'prompt': prompt_i2v,
                    'resolution': resolution_i2v,
                    'duration': duration_i2v
                })

                # 清理临时文件
                if temp_image_path.exists():
                    temp_image_path.unlink()

                st.success("✅ 视频生成成功！")
                st.rerun()

            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"生成失败: {str(e)}")

    # 显示结果
    if st.session_state.i2v_result:
        st.markdown("---")
        st.subheader("🎬 生成结果")

        video_url = st.session_state.i2v_result['url']
        st.markdown(f"**视频 URL**: [{video_url}]({video_url})")
        st.video(video_url)

        st.info("💡 提示：点击视频链接可在新标签页打开，右键保存视频")

# ==================== 文生视频 ====================
with tab3:
    st.header("文生视频 (Text-to-Video)")

    col1, col2 = st.columns([2, 1])

    with col1:
        prompt_t2v = st.text_area(
            "提示词",
            height=150,
            placeholder="描述你想要生成的视频，例如：一只柴犬在草地上奔跑，阳光明媚，春天...",
            help="详细描述视频的内容和场景",
            key="prompt_t2v_input"
        )

        negative_prompt_t2v = st.text_input(
            "负面提示词",
            placeholder="模糊、静止、低质量...",
            help="描述不希望出现的内容",
            key="negative_t2v_input"
        )

    with col2:
        model_t2v = st.selectbox(
            "模型",
            ["wan2.5-t2v-preview"],
            help="选择文生视频模型",
            key="model_t2v_select"
        )

        resolution_t2v = st.selectbox(
            "分辨率",
            ["1080P", "720P", "480P"],
            help="选择视频分辨率",
            key="resolution_t2v_select"
        )

        duration_t2v = st.selectbox(
            "时长（秒）",
            [10, 5],
            help="选择视频时长",
            key="duration_t2v_select"
        )

        seed_t2v = st.number_input(
            "随机种子（可选）",
            min_value=0,
            value=0,
            help="固定种子可重现结果，0 表示随机",
            key="seed_t2v_input"
        )

        watermark_t2v = st.checkbox("添加水印", value=False, key="watermark_t2v_check")

    col_btn1, col_btn2 = st.columns([3, 1])

    with col_btn1:
        generate_t2v = st.button("🎥 生成视频", key="t2v_button", use_container_width=True)

    with col_btn2:
        if st.session_state.t2v_result:
            if st.button("🗑️ 清除结果", key="clear_t2v", use_container_width=True):
                st.session_state.t2v_result = None
                st.rerun()

    if generate_t2v:
        if not client:
            st.error("请先配置 API Key")
        elif not prompt_t2v:
            st.warning("请输入提示词")
        else:
            # 显示预估时间
            estimated_time = duration_t2v * 10
            st.info(f"⏱️ 预计需要 {estimated_time}-{estimated_time+30} 秒，请耐心等待...")

            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                kwargs = {
                    "prompt": prompt_t2v,
                    "model": model_t2v,
                    "resolution": resolution_t2v,
                    "duration": duration_t2v,
                    "watermark": watermark_t2v,
                    "negative_prompt": negative_prompt_t2v,
                }

                if seed_t2v > 0:
                    kwargs["seed"] = seed_t2v

                progress_bar.progress(20)
                status_text.text("正在生成视频...")

                video_url = client.text_to_video(**kwargs)

                progress_bar.progress(100)
                status_text.text("生成完成！")

                # 保存到 session_state
                st.session_state.t2v_result = {
                    'url': video_url,
                    'prompt': prompt_t2v,
                    'params': kwargs
                }

                # 添加到历史记录
                st.session_state.history.append({
                    'type': '文生视频',
                    'time': datetime.now().strftime("%H:%M:%S"),
                    'prompt': prompt_t2v,
                    'resolution': resolution_t2v,
                    'duration': duration_t2v
                })

                st.success("✅ 视频生成成功！")
                st.rerun()

            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"生成失败: {str(e)}")

    # 显示结果
    if st.session_state.t2v_result:
        st.markdown("---")
        st.subheader("🎥 生成结果")

        video_url = st.session_state.t2v_result['url']
        st.markdown(f"**视频 URL**: [{video_url}]({video_url})")
        st.video(video_url)

        st.info("💡 提示：点击视频链接可在新标签页打开，右键保存视频")

# 底部说明
st.markdown("---")
st.markdown("""
### 💡 使用提示

**文生图：**
- 使用详细的描述可以生成更好的图片
- 尝试不同的尺寸和参数组合
- 使用固定种子可以重现相同的结果
- 切换 tab 后结果会保留，不会丢失

**图生视频：**
- 上传清晰的图片效果更好
- 在提示词中详细描述动作和变化
- 使用 [锚定设定]、[动态分层]、[时间轴分层] 等标签可以更好地控制视频生成
- 视频生成需要较长时间，请耐心等待

**文生视频：**
- 描述清晰的场景和动作
- 指定镜头运动和画面变化
- 使用电影级、4K 等关键词提升质量

### 🆕 改进内容

- ✅ **状态保持**：切换 tab 后结果不会丢失
- ✅ **历史记录**：侧边栏显示最近 5 条生成记录
- ✅ **进度提示**：视频生成时显示进度条和预估时间
- ✅ **清除功能**：每个 tab 可单独清除结果
- ✅ **文件保持**：上传的图片在切换 tab 后仍然保留

### 📚 更多资源

- [项目文档](https://github.com/cclank/qwenimg)
- [API 参考](https://github.com/cclank/qwenimg#api-reference)
- [完整教程 Notebook](https://github.com/cclank/qwenimg/blob/main/examples/complete_tutorial.ipynb)
""")
