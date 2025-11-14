"""
QwenImg Web UI - 基于 Streamlit 的 Web 界面

运行方式：
    streamlit run app.py

或者：
    python -m streamlit run app.py
"""

import streamlit as st
import os
from pathlib import Path
from io import BytesIO
import sys

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
            help="详细描述你想要生成的图片内容"
        )

        negative_prompt_t2i = st.text_input(
            "负面提示词",
            placeholder="模糊、粗糙、色彩暗淡...",
            help="描述你不想在图片中出现的内容"
        )

    with col2:
        model_t2i = st.selectbox(
            "模型",
            ["wan2.5-t2i-preview", "wanx-v1"],
            help="选择文生图模型"
        )

        size_t2i = st.selectbox(
            "尺寸",
            ["1024*1024", "1280*720", "720*1280"],
            help="选择图片尺寸"
        )

        n_images = st.slider(
            "生成数量",
            min_value=1,
            max_value=4,
            value=1,
            help="一次生成的图片数量（1-4）"
        )

        seed_t2i = st.number_input(
            "随机种子（可选）",
            min_value=0,
            value=0,
            help="固定种子可重现结果，0 表示随机"
        )

        prompt_extend = st.checkbox("自动扩展提示词", value=True)
        watermark_t2i = st.checkbox("添加水印", value=False)

    if st.button("🎨 生成图片", key="t2i_button"):
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
                        "save": False,  # Web 界面不保存到磁盘
                    }

                    if seed_t2i > 0:
                        kwargs["seed"] = seed_t2i

                    result = client.text_to_image(**kwargs)

                    # 显示结果
                    st.success(f"✅ 成功生成 {n_images} 张图片！")

                    if n_images == 1:
                        st.image(result, caption="生成的图片", use_column_width=True)

                        # 提供下载
                        buf = BytesIO()
                        result.save(buf, format="PNG")
                        st.download_button(
                            label="📥 下载图片",
                            data=buf.getvalue(),
                            file_name="qwenimg_output.png",
                            mime="image/png"
                        )
                    else:
                        cols = st.columns(min(n_images, 2))
                        for i, img in enumerate(result):
                            with cols[i % 2]:
                                st.image(img, caption=f"图片 {i+1}", use_column_width=True)

                                # 提供下载
                                buf = BytesIO()
                                img.save(buf, format="PNG")
                                st.download_button(
                                    label=f"📥 下载图片 {i+1}",
                                    data=buf.getvalue(),
                                    file_name=f"qwenimg_output_{i+1}.png",
                                    mime="image/png",
                                    key=f"download_t2i_{i}"
                                )

                except Exception as e:
                    st.error(f"生成失败: {str(e)}")

# ==================== 图生视频 ====================
with tab2:
    st.header("图生视频 (Image-to-Video)")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "上传图片",
            type=["png", "jpg", "jpeg"],
            help="上传要生成视频的图片"
        )

        if uploaded_file:
            st.image(uploaded_file, caption="上传的图片", use_column_width=True)

        prompt_i2v = st.text_area(
            "提示词（可选）",
            height=120,
            placeholder="描述视频中的动作和变化，例如：角色缓缓转身，云雾翻涌...",
            help="描述视频的动态内容"
        )

        negative_prompt_i2v = st.text_input(
            "负面提示词",
            placeholder="模糊、抖动、失真...",
            help="描述不希望出现的内容"
        )

    with col2:
        model_i2v = st.selectbox(
            "模型",
            ["wan2.5-i2v-preview"],
            help="选择图生视频模型"
        )

        resolution_i2v = st.selectbox(
            "分辨率",
            ["1080P", "720P", "480P"],
            help="选择视频分辨率"
        )

        duration_i2v = st.selectbox(
            "时长（秒）",
            [10, 5],
            help="选择视频时长"
        )

        seed_i2v = st.number_input(
            "随机种子（可选）",
            min_value=0,
            value=0,
            help="固定种子可重现结果，0 表示随机",
            key="seed_i2v"
        )

        watermark_i2v = st.checkbox("添加水印", value=False, key="watermark_i2v")

    if st.button("🎬 生成视频", key="i2v_button"):
        if not client:
            st.error("请先配置 API Key")
        elif not uploaded_file:
            st.warning("请上传图片")
        else:
            with st.spinner("正在生成视频，这可能需要几分钟..."):
                try:
                    # 保存上传的图片到临时文件
                    temp_image_path = Path("/tmp/qwenimg_upload.png")
                    with open(temp_image_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

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

                    video_url = client.image_to_video(**kwargs)

                    # 显示结果
                    st.success("✅ 视频生成成功！")
                    st.markdown(f"**视频 URL**: [{video_url}]({video_url})")
                    st.video(video_url)

                    # 清理临时文件
                    if temp_image_path.exists():
                        temp_image_path.unlink()

                except Exception as e:
                    st.error(f"生成失败: {str(e)}")

# ==================== 文生视频 ====================
with tab3:
    st.header("文生视频 (Text-to-Video)")

    col1, col2 = st.columns([2, 1])

    with col1:
        prompt_t2v = st.text_area(
            "提示词",
            height=150,
            placeholder="描述你想要生成的视频，例如：一只柴犬在草地上奔跑，阳光明媚，春天...",
            help="详细描述视频的内容和场景"
        )

        negative_prompt_t2v = st.text_input(
            "负面提示词",
            placeholder="模糊、静止、低质量...",
            help="描述不希望出现的内容",
            key="negative_t2v"
        )

    with col2:
        model_t2v = st.selectbox(
            "模型",
            ["wan2.5-t2v-preview"],
            help="选择文生视频模型"
        )

        resolution_t2v = st.selectbox(
            "分辨率",
            ["1080P", "720P", "480P"],
            help="选择视频分辨率",
            key="resolution_t2v"
        )

        duration_t2v = st.selectbox(
            "时长（秒）",
            [10, 5],
            help="选择视频时长",
            key="duration_t2v"
        )

        seed_t2v = st.number_input(
            "随机种子（可选）",
            min_value=0,
            value=0,
            help="固定种子可重现结果，0 表示随机",
            key="seed_t2v"
        )

        watermark_t2v = st.checkbox("添加水印", value=False, key="watermark_t2v")

    if st.button("🎥 生成视频", key="t2v_button"):
        if not client:
            st.error("请先配置 API Key")
        elif not prompt_t2v:
            st.warning("请输入提示词")
        else:
            with st.spinner("正在生成视频，这可能需要几分钟..."):
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

                    video_url = client.text_to_video(**kwargs)

                    # 显示结果
                    st.success("✅ 视频生成成功！")
                    st.markdown(f"**视频 URL**: [{video_url}]({video_url})")
                    st.video(video_url)

                except Exception as e:
                    st.error(f"生成失败: {str(e)}")

# 底部说明
st.markdown("---")
st.markdown("""
### 💡 使用提示

**文生图：**
- 使用详细的描述可以生成更好的图片
- 尝试不同的尺寸和参数组合
- 使用固定种子可以重现相同的结果

**图生视频：**
- 上传清晰的图片效果更好
- 在提示词中详细描述动作和变化
- 使用 [锚定设定]、[动态分层]、[时间轴分层] 等标签可以更好地控制视频生成

**文生视频：**
- 描述清晰的场景和动作
- 指定镜头运动和画面变化
- 使用电影级、4K 等关键词提升质量

### 📚 更多资源

- [项目文档](https://github.com/cclank/qwenimg)
- [API 参考](https://github.com/cclank/qwenimg#api-reference)
- [完整教程 Notebook](https://github.com/cclank/qwenimg/blob/main/examples/complete_tutorial.ipynb)
""")
