"""
QwenImg Web UI - 简洁可用版

核心特性：
✅ 所有配置项全保留
✅ 多任务并发执行
✅ 结果自动显示，无需手动刷新
✅ 页面不闪烁，体验流畅
✅ 支持页面刷新
"""

import streamlit as st
import os
import sys
import json
from pathlib import Path
from io import BytesIO
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List
import threading

# 添加项目路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from qwenimg import QwenImg

# ==================== 配置 ====================
DATA_DIR = Path.home() / ".qwenimg"
DATA_DIR.mkdir(exist_ok=True)
TASKS_FILE = DATA_DIR / "tasks.json"

st.set_page_config(
    page_title="QwenImg",
    page_icon="🎨",
    layout="wide"
)

# 自定义 CSS - 禁用页面变浅效果
st.markdown("""
<style>
    /* 禁用 Streamlit 的 stale 元素变浅效果 */
    .stale {
        opacity: 1.0 !important;
    }
    .element-container {
        opacity: 1.0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 持久化 ====================
def load_tasks():
    """加载任务列表"""
    if TASKS_FILE.exists():
        try:
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_tasks(tasks: List[Dict]):
    """保存任务列表"""
    if len(tasks) > 50:
        tasks = tasks[-50:]
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

# ==================== 初始化 ====================
if 'executor' not in st.session_state:
    st.session_state.executor = ThreadPoolExecutor(max_workers=3)

if 'tasks' not in st.session_state:
    st.session_state.tasks = load_tasks()

if 'task_lock' not in st.session_state:
    st.session_state.task_lock = threading.Lock()

# ==================== 任务管理 ====================
def create_task(task_type: str, params: Dict[str, Any]) -> str:
    """创建新任务"""
    task_id = f"{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    task = {
        'id': task_id,
        'type': task_type,
        'status': 'running',
        'params': params,
        'result': None,
        'error': None,
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    with st.session_state.task_lock:
        st.session_state.tasks.append(task)
        save_tasks(st.session_state.tasks)
    return task_id

def update_task(task_id: str, **kwargs):
    """更新任务"""
    with st.session_state.task_lock:
        for task in st.session_state.tasks:
            if task['id'] == task_id:
                task.update(kwargs)
                save_tasks(st.session_state.tasks)
                break

def get_tasks_by_type(task_type: str) -> List[Dict]:
    """获取指定类型的任务（倒序）"""
    with st.session_state.task_lock:
        tasks = [t for t in st.session_state.tasks if t['type'] == task_type]
    return list(reversed(tasks))

def has_running_tasks() -> bool:
    """检查是否有运行中的任务"""
    with st.session_state.task_lock:
        return any(t['status'] == 'running' for t in st.session_state.tasks)

# ==================== 任务执行 ====================
def run_task(task_id: str, client: QwenImg, task_type: str, params: Dict[str, Any]):
    """后台执行任务"""
    try:
        if task_type == 't2i':
            result = client.text_to_image(**params)
            result_data = {'images': result if isinstance(result, list) else [result]}
        elif task_type == 'i2v':
            url = client.image_to_video(**params)
            result_data = {'url': url}
        elif task_type == 't2v':
            url = client.text_to_video(**params)
            result_data = {'url': url}
        else:
            raise ValueError(f"Unknown task type: {task_type}")

        update_task(task_id, status='completed', result=result_data)

    except Exception as e:
        update_task(task_id, status='error', error=str(e))

# ==================== 客户端 ====================
@st.cache_resource
def init_client(api_key: str, region: str):
    try:
        return QwenImg(api_key=api_key, region=region)
    except Exception as e:
        st.error(f"初始化失败: {str(e)}")
        return None

# ==================== UI ====================
st.title("🎨 QwenImg")
st.caption("简洁可用的图片视频生成工具")

# 顶部刷新按钮
col_refresh, col_stats = st.columns([1, 4])
with col_refresh:
    if st.button("🔄 刷新结果", use_container_width=True):
        st.rerun()

with col_stats:
    running_count = len([t for t in st.session_state.tasks if t['status'] == 'running'])
    if running_count > 0:
        st.info(f"⏳ 正在执行 {running_count} 个任务，点击左侧刷新按钮查看最新结果")

st.divider()

# 侧边栏
with st.sidebar:
    st.header("⚙️ 配置")
    api_key = st.text_input(
        "API Key",
        type="password",
        value=os.getenv("DASHSCOPE_API_KEY", ""),
    )
    region = st.selectbox("地域", ["beijing", "singapore"])

    st.divider()

    # 统计信息
    st.header("📊 统计")
    total = len(st.session_state.tasks)
    running = len([t for t in st.session_state.tasks if t['status'] == 'running'])
    completed = len([t for t in st.session_state.tasks if t['status'] == 'completed'])
    errors = len([t for t in st.session_state.tasks if t['status'] == 'error'])

    col1, col2 = st.columns(2)
    with col1:
        st.metric("总任务", total)
        st.metric("运行中", running)
    with col2:
        st.metric("已完成", completed)
        st.metric("失败", errors)

    if st.button("🗑️ 清空所有任务", use_container_width=True):
        st.session_state.tasks = []
        save_tasks([])
        st.rerun()

    st.divider()
    st.caption("[GitHub](https://github.com/cclank/qwenimg) | by 岚叔")

# 初始化客户端
client = init_client(api_key, region) if api_key else None

if not client:
    st.warning("⚠️ 请在侧边栏输入 API Key")
    st.stop()

# ==================== 主界面 ====================
tab1, tab2, tab3 = st.tabs(["📝 文生图", "🎬 图生视频", "🎥 文生视频"])

# ==================== 文生图 ====================
with tab1:
    st.header("文生图 (Text-to-Image)")

    with st.form("t2i_form"):
        col1, col2 = st.columns([2, 1])

        with col1:
            prompt = st.text_area(
                "提示词",
                height=120,
                placeholder="一只可爱的橘猫坐在窗台上，阳光洒在它身上...",
            )
            negative_prompt = st.text_input(
                "负面提示词（可选）",
                placeholder="模糊、粗糙、色彩暗淡...",
            )

        with col2:
            model = st.selectbox("模型", ["wan2.5-t2i-preview", "wanx-v1"])
            size = st.selectbox("尺寸", ["1024*1024", "1280*720", "720*1280"])
            n = st.slider("生成数量", 1, 4, 1)
            seed = st.number_input("随机种子（0=随机）", min_value=0, value=0)
            prompt_extend = st.checkbox("自动扩展提示词", value=True)
            watermark = st.checkbox("添加水印", value=False)

        submitted = st.form_submit_button("🎨 生成图片", use_container_width=True)

        if submitted:
            if not prompt:
                st.warning("请输入提示词")
            else:
                params = {
                    'prompt': prompt,
                    'model': model,
                    'size': size,
                    'n': n,
                    'negative_prompt': negative_prompt,
                    'prompt_extend': prompt_extend,
                    'watermark': watermark,
                    'save': False
                }
                if seed > 0:
                    params['seed'] = seed

                task_id = create_task('t2i', params)
                st.session_state.executor.submit(run_task, task_id, client, 't2i', params)
                st.success(f"✅ 任务已提交：{task_id}")

    st.divider()
    st.subheader("任务列表")

    # 显示任务列表
    tasks = get_tasks_by_type('t2i')

    if not tasks:
        st.info("暂无任务，提交任务后会显示在这里")
    else:
        for task in tasks:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])

                with col1:
                    st.markdown(f"**{task['id']}**")
                    st.caption(f"创建时间: {task['created_at']}")

                with col2:
                    if task['status'] == 'running':
                        st.warning("⏳ 运行中")
                    elif task['status'] == 'error':
                        st.error("❌ 失败")
                    elif task['status'] == 'completed':
                        st.success("✅ 完成")

                with col3:
                    with st.expander("参数"):
                        st.caption(f"提示词: {task['params']['prompt'][:30]}...")
                        st.caption(f"模型: {task['params']['model']}")
                        st.caption(f"尺寸: {task['params']['size']}")

                # 显示结果
                if task['status'] == 'error':
                    st.error(task['error'])
                elif task['status'] == 'completed' and task['result']:
                    images = task['result']['images']
                    cols = st.columns(min(len(images), 4))
                    for i, img in enumerate(images):
                        with cols[i % 4]:
                            st.image(img, use_container_width=True)
                            buf = BytesIO()
                            img.save(buf, format="PNG")
                            st.download_button(
                                "📥 下载",
                                buf.getvalue(),
                                f"{task['id']}_{i+1}.png",
                                "image/png",
                                key=f"dl_{task['id']}_{i}"
                            )

                st.divider()

# ==================== 图生视频 ====================
with tab2:
    st.header("图生视频 (Image-to-Video)")

    with st.form("i2v_form"):
        col1, col2 = st.columns([2, 1])

        with col1:
            uploaded = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"])
            if uploaded:
                st.image(uploaded, caption="预览", use_container_width=True)

            prompt = st.text_area(
                "提示词（可选）",
                height=100,
                placeholder="描述视频中的动作和变化...",
            )
            negative_prompt = st.text_input(
                "负面提示词（可选）",
                placeholder="模糊、抖动、失真...",
            )

        with col2:
            model = st.selectbox("模型", ["wan2.5-i2v-preview"])
            resolution = st.selectbox("分辨率", ["1080P", "720P", "480P"])
            duration = st.selectbox("时长", [10, 5])
            seed = st.number_input("随机种子（0=随机）", min_value=0, value=0, key="i2v_seed")
            watermark = st.checkbox("添加水印", value=False, key="i2v_watermark")

        submitted = st.form_submit_button("🎬 生成视频", use_container_width=True)

        if submitted:
            if not uploaded:
                st.warning("请上传图片")
            else:
                temp_path = DATA_DIR / f"temp_i2v_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                with open(temp_path, "wb") as f:
                    f.write(uploaded.getbuffer())

                params = {
                    'image': str(temp_path),
                    'model': model,
                    'prompt': prompt,
                    'negative_prompt': negative_prompt,
                    'resolution': resolution,
                    'duration': duration,
                    'watermark': watermark,
                }
                if seed > 0:
                    params['seed'] = seed

                task_id = create_task('i2v', params)
                st.session_state.executor.submit(run_task, task_id, client, 'i2v', params)
                st.success(f"✅ 任务已提交：{task_id}")

    st.divider()
    st.subheader("任务列表")

    tasks = get_tasks_by_type('i2v')

    if not tasks:
        st.info("暂无任务，提交任务后会显示在这里")
    else:
        for task in tasks:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])

                with col1:
                    st.markdown(f"**{task['id']}**")
                    st.caption(f"创建时间: {task['created_at']}")

                with col2:
                    if task['status'] == 'running':
                        st.warning("⏳ 运行中")
                    elif task['status'] == 'error':
                        st.error("❌ 失败")
                    elif task['status'] == 'completed':
                        st.success("✅ 完成")

                with col3:
                    with st.expander("参数"):
                        st.caption(f"分辨率: {task['params']['resolution']}")
                        st.caption(f"时长: {task['params']['duration']}秒")

                if task['status'] == 'error':
                    st.error(task['error'])
                elif task['status'] == 'completed' and task['result']:
                    url = task['result']['url']
                    st.video(url)
                    st.caption(f"[视频链接]({url})")

                st.divider()

# ==================== 文生视频 ====================
with tab3:
    st.header("文生视频 (Text-to-Video)")

    with st.form("t2v_form"):
        col1, col2 = st.columns([2, 1])

        with col1:
            prompt = st.text_area(
                "提示词",
                height=120,
                placeholder="一只柴犬在草地上奔跑，阳光明媚...",
            )
            negative_prompt = st.text_input(
                "负面提示词（可选）",
                placeholder="模糊、静止、低质量...",
            )

        with col2:
            model = st.selectbox("模型", ["wan2.5-t2v-preview"])
            resolution = st.selectbox("分辨率", ["1080P", "720P", "480P"], key="t2v_res")
            duration = st.selectbox("时长", [10, 5], key="t2v_dur")
            seed = st.number_input("随机种子（0=随机）", min_value=0, value=0, key="t2v_seed")
            watermark = st.checkbox("添加水印", value=False, key="t2v_watermark")

        submitted = st.form_submit_button("🎥 生成视频", use_container_width=True)

        if submitted:
            if not prompt:
                st.warning("请输入提示词")
            else:
                params = {
                    'prompt': prompt,
                    'model': model,
                    'negative_prompt': negative_prompt,
                    'resolution': resolution,
                    'duration': duration,
                    'watermark': watermark,
                }
                if seed > 0:
                    params['seed'] = seed

                task_id = create_task('t2v', params)
                st.session_state.executor.submit(run_task, task_id, client, 't2v', params)
                st.success(f"✅ 任务已提交：{task_id}")

    st.divider()
    st.subheader("任务列表")

    tasks = get_tasks_by_type('t2v')

    if not tasks:
        st.info("暂无任务，提交任务后会显示在这里")
    else:
        for task in tasks:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])

                with col1:
                    st.markdown(f"**{task['id']}**")
                    st.caption(f"创建时间: {task['created_at']}")

                with col2:
                    if task['status'] == 'running':
                        st.warning("⏳ 运行中")
                    elif task['status'] == 'error':
                        st.error("❌ 失败")
                    elif task['status'] == 'completed':
                        st.success("✅ 完成")

                with col3:
                    with st.expander("参数"):
                        st.caption(f"提示词: {task['params']['prompt'][:30]}...")
                        st.caption(f"分辨率: {task['params']['resolution']}")
                        st.caption(f"时长: {task['params']['duration']}秒")

                if task['status'] == 'error':
                    st.error(task['error'])
                elif task['status'] == 'completed' and task['result']:
                    url = task['result']['url']
                    st.video(url)
                    st.caption(f"[视频链接]({url})")

                st.divider()

# 自动刷新（仅当有运行中任务时）
if has_running_tasks():
    st.markdown("""
    <script>
        setTimeout(function() {
            window.parent.location.reload();
        }, 3000);
    </script>
    """, unsafe_allow_html=True)
