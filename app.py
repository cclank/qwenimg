"""
QwenImg Web UI - 简洁可用版

设计思路：
- 完全基于文件持久化，不依赖 session_state
- 后台线程直接读写文件
- 主线程每次渲染时重新加载文件
- 使用文件锁避免并发冲突
- 提示词与效果在同一页面，设置放右侧可折叠
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

    /* 限制图片和视频的最大高度 */
    img, video {
        max-height: 70vh !important;
        object-fit: contain !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 初始化状态 ====================
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None

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
            with open(TASKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(tasks[-50:], f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"保存任务失败: {e}")

def get_tasks_by_type(task_type: str) -> List[Dict]:
    """获取指定类型的任务"""
    tasks = load_tasks()
    return [t for t in tasks if t['type'] == task_type]

def create_task(task_type: str, params: Dict) -> str:
    """创建新任务"""
    task_id = f"{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    task = {
        'id': task_id,
        'type': task_type,
        'status': 'running',
        'params': params,
        'result': None,
        'error': None,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    return task_id

def update_task(task_id: str, updates: Dict):
    """更新任务状态"""
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task.update(updates)
            break
    save_tasks(tasks)

# ==================== 线程池 ====================
if 'executor' not in st.session_state:
    st.session_state.executor = ThreadPoolExecutor(max_workers=3)

# ==================== 后台任务执行 ====================
def run_task(task_id: str, api_key: str, region: str, task_type: str, params: Dict):
    """在后台线程执行任务"""
    try:
        client = QwenImg(api_key=api_key, region=region)

        if task_type == 't2i':
            # 让 SDK 自动保存到指定目录并返回文件路径
            params['save'] = True
            params['return_pil'] = False
            params['output_dir'] = str(DATA_DIR)

            image_paths = client.text_to_image(**params)
            # text_to_image 返回的是文件路径列表
            if not isinstance(image_paths, list):
                image_paths = [image_paths]

            update_task(task_id, {
                'status': 'completed',
                'result': {'image_paths': image_paths}
            })

        elif task_type == 'i2v':
            # image_to_video 返回的是视频 URL 字符串
            video_url = client.image_to_video(**params)
            update_task(task_id, {
                'status': 'completed',
                'result': {'url': video_url}
            })

        elif task_type == 't2v':
            # text_to_video 返回的是视频 URL 字符串
            video_url = client.text_to_video(**params)
            update_task(task_id, {
                'status': 'completed',
                'result': {'url': video_url}
            })

    except Exception as e:
        update_task(task_id, {
            'status': 'error',
            'error': str(e)
        })

# ==================== 侧边栏 ====================
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
    st.metric("📋 总任务", total)
    st.metric("⏳ 运行中", running)
    st.metric("✅ 已完成", completed)
    st.metric("❌ 失败", errors)

    st.divider()

    if st.button("🗑️ 清空所有", use_container_width=True):
        save_tasks([])
        # 删除所有图片文件
        for img_file in DATA_DIR.glob("*.png"):
            img_file.unlink()
        st.rerun()

    st.divider()
    st.markdown("**GitHub by 岚叔**")
    st.caption("[github.com/cclank/qwenimg](https://github.com/cclank/qwenimg)")

if not api_key:
    st.warning("⚠️ 请在侧边栏输入 API Key")
    st.stop()

# ==================== 智能刷新机制 ====================
# 只在有"最近提交的运行中任务"时才刷新，避免一直闪烁
all_tasks = load_tasks()
now = datetime.now()

# 找出最近60秒内创建且仍在运行的任务
recent_running_tasks = []
for t in all_tasks:
    if t['status'] == 'running':
        try:
            created_time = datetime.strptime(t['created_at'], '%Y-%m-%d %H:%M:%S')
            age_seconds = (now - created_time).total_seconds()
            if age_seconds < 60:  # 只刷新最近60秒内的任务
                recent_running_tasks.append(t)
        except:
            pass

if recent_running_tasks:
    # 只在有最近任务时才刷新
    st.info(f"⏳ 有 {len(recent_running_tasks)} 个任务正在处理中，页面将自动更新...")
    time.sleep(5)  # 5秒刷新一次
    st.rerun()

# ==================== 主界面 ====================
tab1, tab2, tab3 = st.tabs(["📝 文生图", "🎬 图生视频", "🎥 文生视频"])

# ==================== 文生图 ====================
with tab1:
    # 左右分栏：左侧70%提示词+结果，右侧30%设置
    left_col, right_col = st.columns([7, 3])

    with left_col:
        st.subheader("提示词")
        prompt = st.text_area("描述你想生成的图片", height=120, placeholder="一只可爱的橘猫...", key="t2i_prompt")
        negative_prompt = st.text_input("负面提示词（可选）", placeholder="模糊、粗糙...", key="t2i_neg")

    with right_col:
        st.subheader("设置")
        with st.expander("⚙️ 高级设置", expanded=True):
            model = st.selectbox("模型", ["wan2.5-t2i-preview", "wanx-v1"], key="t2i_model")
            size = st.selectbox("尺寸", ["1024*1024", "1280*720", "720*1280"], key="t2i_size")
            n = st.slider("数量", 1, 4, 1, key="t2i_n")
            seed = st.number_input("随机种子（0=随机）", min_value=0, value=0, key="t2i_seed")
            prompt_extend = st.checkbox("自动扩展提示词", value=True, key="t2i_extend")
            watermark = st.checkbox("添加水印", value=False, key="t2i_wm")

    # 生成按钮放在提示词下方
    with left_col:
        if st.button("🎨 开始生成", use_container_width=True, type="primary"):
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
                    'watermark': watermark
                }
                if seed > 0:
                    params['seed'] = seed

                task_id = create_task('t2i', params)
                st.session_state.executor.submit(run_task, task_id, api_key, region, 't2i', params)
                st.success(f"✅ 任务已提交（ID: {task_id[-8:]}）")
                time.sleep(0.5)  # 短暂延迟，让用户看到提示
                st.rerun()

    st.divider()

    # 任务列表和结果展示
    with left_col:
        st.subheader("生成结果")
        tasks = get_tasks_by_type('t2i')
        if not tasks:
            st.info("暂无任务，开始创作吧！")
        else:
            for task in reversed(tasks):  # 最新的在上面
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{task['params']['prompt'][:50]}...**" if len(task['params']['prompt']) > 50 else f"**{task['params']['prompt']}**")
                        st.caption(f"{task['created_at']} · {task['id']}")
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
                                            key=f"dl_{task['id']}_{i}"
                                        )
                    st.divider()

# ==================== 图生视频 ====================
with tab2:
    # 左右分栏
    left_col, right_col = st.columns([7, 3])

    with left_col:
        st.subheader("上传图片")
        uploaded = st.file_uploader("选择图片", type=['png', 'jpg', 'jpeg'], key="i2v_upload")

        # 立即显示上传的图片预览
        if uploaded:
            st.markdown("**图片预览**")
            st.image(uploaded, use_container_width=True)
            st.session_state.uploaded_image = uploaded

        st.subheader("提示词")
        prompt = st.text_area("描述视频动作（可选）", height=100, placeholder="描述视频动作...", key="i2v_prompt")
        negative_prompt = st.text_input("负面提示词（可选）", placeholder="模糊、抖动...", key="i2v_neg")

    with right_col:
        st.subheader("设置")
        with st.expander("⚙️ 高级设置", expanded=True):
            model = st.selectbox("模型", ["wan2.5-i2v-preview"], key="i2v_model")
            resolution = st.selectbox("分辨率", ["1080P", "720P", "480P"], key="i2v_res")
            duration = st.selectbox("时长", [10, 5], key="i2v_dur")
            seed = st.number_input("随机种子（0=随机）", min_value=0, value=0, key="i2v_seed")
            watermark = st.checkbox("添加水印", value=False, key="i2v_wm")

    # 生成按钮放在提示词下方
    with left_col:
        if st.button("🎬 开始生成", use_container_width=True, type="primary"):
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
                st.success(f"✅ 任务已提交（ID: {task_id[-8:]}）")
                time.sleep(0.5)
                st.rerun()

    st.divider()

    # 任务列表和结果展示
    with left_col:
        st.subheader("生成结果")
        tasks = get_tasks_by_type('i2v')
        if not tasks:
            st.info("暂无任务，开始创作吧！")
        else:
            for task in reversed(tasks):
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        prompt_text = task['params'].get('prompt', '(无提示词)')
                        st.markdown(f"**{prompt_text[:50]}...**" if len(prompt_text) > 50 else f"**{prompt_text}**")
                        st.caption(f"{task['created_at']} · {task['id']}")
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
                        st.video(task['result']['url'])

                    st.divider()

# ==================== 文生视频 ====================
with tab3:
    # 左右分栏
    left_col, right_col = st.columns([7, 3])

    with left_col:
        st.subheader("提示词")
        prompt = st.text_area("描述你想生成的视频", height=120, placeholder="海浪拍打着沙滩...", key="t2v_prompt")
        negative_prompt = st.text_input("负面提示词（可选）", placeholder="模糊、抖动...", key="t2v_neg")

    with right_col:
        st.subheader("设置")
        with st.expander("⚙️ 高级设置", expanded=True):
            model = st.selectbox("模型", ["wan2.5-t2v-preview"], key="t2v_model")
            resolution = st.selectbox("分辨率", ["1080P", "720P", "480P"], key="t2v_res")
            duration = st.selectbox("时长", [10, 5], key="t2v_dur")
            seed = st.number_input("随机种子（0=随机）", min_value=0, value=0, key="t2v_seed")
            watermark = st.checkbox("添加水印", value=False, key="t2v_wm")

    # 生成按钮放在提示词下方
    with left_col:
        if st.button("🎥 开始生成", use_container_width=True, type="primary"):
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
                st.success(f"✅ 任务已提交（ID: {task_id[-8:]}）")
                time.sleep(0.5)
                st.rerun()

    st.divider()

    # 任务列表和结果展示
    with left_col:
        st.subheader("生成结果")
        tasks = get_tasks_by_type('t2v')
        if not tasks:
            st.info("暂无任务，开始创作吧！")
        else:
            for task in reversed(tasks):
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{task['params']['prompt'][:50]}...**" if len(task['params']['prompt']) > 50 else f"**{task['params']['prompt']}**")
                        st.caption(f"{task['created_at']} · {task['id']}")
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
                        st.video(task['result']['url'])

                    st.divider()
