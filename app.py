"""
QwenImg Web UI - 简洁可用版

设计思路：
- 完全基于文件持久化，不依赖 session_state
- 后台线程直接读写文件
- 主线程每次渲染时重新加载文件
- 使用文件锁避免并发冲突
"""

import streamlit as st
import os
import sys
import json
from pathlib import Path
from io import BytesIO
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Optional
import time
import filelock

# 添加项目路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from qwenimg import QwenImg

# ==================== 配置 ====================
DATA_DIR = Path.home() / ".qwenimg"
DATA_DIR.mkdir(exist_ok=True)
TASKS_FILE = DATA_DIR / "tasks.json"
LOCK_FILE = DATA_DIR / "tasks.lock"

st.set_page_config(
    page_title="QwenImg",
    page_icon="🎨",
    layout="wide"
)

# 自定义 CSS
st.markdown("""
<style>
    .stale { opacity: 1.0 !important; }
    .element-container { opacity: 1.0 !important; }
    [data-testid="stale-element-container"] { opacity: 1.0 !important; }
    * { transition: none !important; }
</style>
""", unsafe_allow_html=True)

# ==================== 初始化状态 ====================
if 'status_filter' not in st.session_state:
    st.session_state.status_filter = None  # None, 'running', 'completed', 'error'

# ==================== 文件操作（线程安全）====================
def load_tasks() -> List[Dict]:
    """从文件加载任务（线程安全）"""
    lock = filelock.FileLock(str(LOCK_FILE), timeout=10)
    try:
        with lock:
            if TASKS_FILE.exists():
                with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
    except Exception as e:
        st.error(f"加载任务失败: {e}")
    return []

def save_tasks(tasks: List[Dict]):
    """保存任务到文件（线程安全）"""
    lock = filelock.FileLock(str(LOCK_FILE), timeout=10)
    try:
        with lock:
            # 只保留最近 50 个任务
            if len(tasks) > 50:
                tasks = tasks[-50:]
            with open(TASKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"保存任务失败: {e}")

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

    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    return task_id

def update_task(task_id: str, **kwargs):
    """更新任务状态"""
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task.update(kwargs)
            break
    save_tasks(tasks)

def get_tasks_by_type(task_type: str, status_filter: Optional[str] = None) -> List[Dict]:
    """获取指定类型的任务，支持状态筛选"""
    tasks = load_tasks()
    filtered = [t for t in tasks if t['type'] == task_type]

    # 应用状态筛选
    if status_filter:
        filtered = [t for t in filtered if t['status'] == status_filter]

    return list(reversed(filtered))  # 最新的在前

def has_running_tasks() -> bool:
    """检查是否有运行中的任务"""
    tasks = load_tasks()
    return any(t['status'] == 'running' for t in tasks)

# ==================== 任务执行 ====================
def run_task(task_id: str, api_key: str, region: str, task_type: str, params: Dict[str, Any]):
    """后台执行任务"""
    try:
        # 初始化客户端
        client = QwenImg(api_key=api_key, region=region)

        # 执行任务
        if task_type == 't2i':
            result = client.text_to_image(**params)
            # 保存图片到本地，存储路径
            images = result if isinstance(result, list) else [result]
            image_paths = []
            for i, img in enumerate(images):
                img_path = DATA_DIR / f"{task_id}_{i}.png"
                img.save(img_path)
                image_paths.append(str(img_path))
            result_data = {'image_paths': image_paths}

        elif task_type == 'i2v':
            url = client.image_to_video(**params)
            result_data = {'url': url}

        elif task_type == 't2v':
            url = client.text_to_video(**params)
            result_data = {'url': url}
        else:
            raise ValueError(f"Unknown task type: {task_type}")

        # 更新任务状态为完成
        update_task(task_id, status='completed', result=result_data)

    except Exception as e:
        # 更新任务状态为失败
        update_task(task_id, status='error', error=str(e))

# ==================== 全局线程池 ====================
if 'executor' not in st.session_state:
    st.session_state.executor = ThreadPoolExecutor(max_workers=3)

# ==================== 客户端 ====================
@st.cache_resource
def init_client(api_key: str, region: str):
    try:
        return QwenImg(api_key=api_key, region=region)
    except:
        return None

# ==================== UI ====================
st.title("🎨 QwenImg")
st.caption("简洁可用的图片视频生成工具")

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
    all_tasks = load_tasks()
    total = len(all_tasks)
    running = len([t for t in all_tasks if t['status'] == 'running'])
    completed = len([t for t in all_tasks if t['status'] == 'completed'])
    errors = len([t for t in all_tasks if t['status'] == 'error'])

    st.header("📊 统计")

    # 可点击的统计指标
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"📋 总任务\n{total}", use_container_width=True, key="filter_all"):
            st.session_state.status_filter = None
            st.rerun()
        if st.button(f"⏳ 运行中\n{running}", use_container_width=True, key="filter_running",
                     type="primary" if st.session_state.status_filter == 'running' else "secondary"):
            st.session_state.status_filter = 'running'
            st.rerun()
    with col2:
        if st.button(f"✅ 已完成\n{completed}", use_container_width=True, key="filter_completed",
                     type="primary" if st.session_state.status_filter == 'completed' else "secondary"):
            st.session_state.status_filter = 'completed'
            st.rerun()
        if st.button(f"❌ 失败\n{errors}", use_container_width=True, key="filter_error",
                     type="primary" if st.session_state.status_filter == 'error' else "secondary"):
            st.session_state.status_filter = 'error'
            st.rerun()

    # 显示当前筛选状态
    if st.session_state.status_filter:
        filter_text = {
            'running': '⏳ 运行中',
            'completed': '✅ 已完成',
            'error': '❌ 失败'
        }
        st.info(f"当前筛选: {filter_text[st.session_state.status_filter]}")

    st.divider()

    if st.button("🗑️ 清空所有", use_container_width=True):
        save_tasks([])
        # 删除所有图片文件
        for img_file in DATA_DIR.glob("*.png"):
            img_file.unlink()
        st.rerun()

    st.divider()
    st.caption("[GitHub](https://github.com/cclank/qwenimg)")

if not api_key:
    st.warning("⚠️ 请在侧边栏输入 API Key")
    st.stop()

st.divider()

# ==================== 主界面 ====================
tab1, tab2, tab3 = st.tabs(["📝 文生图", "🎬 图生视频", "🎥 文生视频"])

# ==================== 文生图 ====================
with tab1:
    st.header("文生图")

    with st.form("t2i_form"):
        col1, col2 = st.columns([2, 1])

        with col1:
            prompt = st.text_area("提示词", height=120, placeholder="一只可爱的橘猫...")
            negative_prompt = st.text_input("负面提示词（可选）", placeholder="模糊、粗糙...")

        with col2:
            model = st.selectbox("模型", ["wan2.5-t2i-preview", "wanx-v1"])
            size = st.selectbox("尺寸", ["1024*1024", "1280*720", "720*1280"])
            n = st.slider("数量", 1, 4, 1)
            seed = st.number_input("随机种子（0=随机）", min_value=0, value=0)
            prompt_extend = st.checkbox("自动扩展提示词", value=True)
            watermark = st.checkbox("添加水印", value=False)

        if st.form_submit_button("🎨 生成", use_container_width=True):
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
                st.session_state.executor.submit(run_task, task_id, api_key, region, 't2i', params)
                st.success(f"✅ 任务已提交")
                st.rerun()

    st.divider()
    st.subheader("任务列表")

    tasks = get_tasks_by_type('t2i', st.session_state.status_filter)
    if not tasks:
        st.info("暂无任务" if not st.session_state.status_filter else f"暂无{st.session_state.status_filter}状态的任务")
    else:
        for task in tasks:
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{task['id']}**")
                    st.caption(task['created_at'])
                with col2:
                    if task['status'] == 'running':
                        st.warning("⏳ 运行中")
                    elif task['status'] == 'error':
                        st.error("❌ 失败")
                    elif task['status'] == 'completed':
                        st.success("✅ 完成")

                if task['status'] == 'error':
                    st.error(task['error'])
                elif task['status'] == 'completed' and task['result']:
                    image_paths = task['result']['image_paths']

                    # 使用 3/4 屏幕宽度显示图片
                    _, col_center, _ = st.columns([0.125, 0.75, 0.125])
                    with col_center:
                        cols = st.columns(min(len(image_paths), 4))
                        for i, img_path in enumerate(image_paths):
                            if Path(img_path).exists():
                                with cols[i % 4]:
                                    st.image(img_path, use_container_width=True)
                                    with open(img_path, 'rb') as f:
                                        st.download_button(
                                            "📥",
                                            f.read(),
                                            f"{task['id']}_{i+1}.png",
                                            "image/png",
                                            key=f"dl_{task['id']}_{i}"
                                        )
                st.divider()

# ==================== 图生视频 ====================
with tab2:
    st.header("图生视频")

    with st.form("i2v_form"):
        col1, col2 = st.columns([2, 1])

        with col1:
            uploaded = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"])

            # 上传后立即显示预览（3/4 宽度）
            if uploaded:
                st.markdown("### 📸 图片预览")
                _, col_preview, _ = st.columns([0.125, 0.75, 0.125])
                with col_preview:
                    st.image(uploaded, use_container_width=True)
                st.success("✅ 图片已上传")

            prompt = st.text_area("提示词（可选）", height=100, placeholder="描述视频动作...")
            negative_prompt = st.text_input("负面提示词（可选）", placeholder="模糊、抖动...")

        with col2:
            model = st.selectbox("模型", ["wan2.5-i2v-preview"])
            resolution = st.selectbox("分辨率", ["1080P", "720P", "480P"])
            duration = st.selectbox("时长", [10, 5])
            seed = st.number_input("随机种子", min_value=0, value=0, key="i2v_seed")
            watermark = st.checkbox("水印", value=False, key="i2v_wm")

        if st.form_submit_button("🎬 生成", use_container_width=True):
            if not uploaded:
                st.warning("请上传图片")
            else:
                temp_path = DATA_DIR / f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
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
                st.session_state.executor.submit(run_task, task_id, api_key, region, 'i2v', params)
                st.success("✅ 任务已提交")
                st.rerun()

    st.divider()
    st.subheader("任务列表")

    tasks = get_tasks_by_type('i2v', st.session_state.status_filter)
    if not tasks:
        st.info("暂无任务" if not st.session_state.status_filter else f"暂无{st.session_state.status_filter}状态的任务")
    else:
        for task in tasks:
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{task['id']}**")
                    st.caption(task['created_at'])
                with col2:
                    if task['status'] == 'running':
                        st.warning("⏳ 运行中")
                    elif task['status'] == 'error':
                        st.error("❌ 失败")
                    elif task['status'] == 'completed':
                        st.success("✅ 完成")

                if task['status'] == 'error':
                    st.error(task['error'])
                elif task['status'] == 'completed' and task['result']:
                    # 使用 3/4 屏幕宽度显示视频
                    _, col_center, _ = st.columns([0.125, 0.75, 0.125])
                    with col_center:
                        st.video(task['result']['url'])
                    st.caption(f"[下载]({task['result']['url']})")
                st.divider()

# ==================== 文生视频 ====================
with tab3:
    st.header("文生视频")

    with st.form("t2v_form"):
        col1, col2 = st.columns([2, 1])

        with col1:
            prompt = st.text_area("提示词", height=120, placeholder="一只柴犬...")
            negative_prompt = st.text_input("负面提示词（可选）", placeholder="模糊、静止...")

        with col2:
            model = st.selectbox("模型", ["wan2.5-t2v-preview"])
            resolution = st.selectbox("分辨率", ["1080P", "720P", "480P"], key="t2v_res")
            duration = st.selectbox("时长", [10, 5], key="t2v_dur")
            seed = st.number_input("随机种子", min_value=0, value=0, key="t2v_seed")
            watermark = st.checkbox("水印", value=False, key="t2v_wm")

        if st.form_submit_button("🎥 生成", use_container_width=True):
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
                st.session_state.executor.submit(run_task, task_id, api_key, region, 't2v', params)
                st.success("✅ 任务已提交")
                st.rerun()

    st.divider()
    st.subheader("任务列表")

    tasks = get_tasks_by_type('t2v', st.session_state.status_filter)
    if not tasks:
        st.info("暂无任务" if not st.session_state.status_filter else f"暂无{st.session_state.status_filter}状态的任务")
    else:
        for task in tasks:
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{task['id']}**")
                    st.caption(task['created_at'])
                with col2:
                    if task['status'] == 'running':
                        st.warning("⏳ 运行中")
                    elif task['status'] == 'error':
                        st.error("❌ 失败")
                    elif task['status'] == 'completed':
                        st.success("✅ 完成")

                if task['status'] == 'error':
                    st.error(task['error'])
                elif task['status'] == 'completed' and task['result']:
                    # 使用 3/4 屏幕宽度显示视频
                    _, col_center, _ = st.columns([0.125, 0.75, 0.125])
                    with col_center:
                        st.video(task['result']['url'])
                    st.caption(f"[下载]({task['result']['url']})")
                st.divider()

# ==================== 自动刷新 ====================
if has_running_tasks():
    time.sleep(2)
    st.rerun()
