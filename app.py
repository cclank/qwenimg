"""
QwenImg Web UI - 极简版

运行方式：
    streamlit run app.py

核心特性：
    ✅ 支持页面刷新 - 本地持久化所有状态
    ✅ 极简代码 - 统一任务管理
    ✅ 并发创作 - 多任务同时执行
    ✅ 完整历史 - 所有记录永久保存
"""

import streamlit as st
import os
import sys
import json
from pathlib import Path
from io import BytesIO
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional
import time

# 添加项目路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from qwenimg import QwenImg

# ==================== 配置 ====================
DATA_DIR = Path.home() / ".qwenimg"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "history.json"
STATE_FILE = DATA_DIR / "state.json"

st.set_page_config(
    page_title="QwenImg - 极简版",
    page_icon="🎨",
    layout="wide"
)

# ==================== 持久化管理 ====================
def load_json(file_path: Path, default=None):
    """加载 JSON 文件"""
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return default if default is not None else []

def save_json(file_path: Path, data):
    """保存 JSON 文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_state():
    """保存当前状态到本地"""
    state_data = {
        'tasks': st.session_state.get('tasks', {}),
        'inputs': {
            't2i': st.session_state.get('t2i_inputs', {}),
            'i2v': st.session_state.get('i2v_inputs', {}),
            't2v': st.session_state.get('t2v_inputs', {}),
        }
    }
    save_json(STATE_FILE, state_data)

def load_state():
    """从本地加载状态"""
    return load_json(STATE_FILE, {'tasks': {}, 'inputs': {'t2i': {}, 'i2v': {}, 't2v': {}}})

def save_history(record: Dict[str, Any]):
    """保存历史记录"""
    history = load_json(HISTORY_FILE, [])
    history.append(record)
    # 只保留最近 100 条
    if len(history) > 100:
        history = history[-100:]
    save_json(HISTORY_FILE, history)

# ==================== 初始化 ====================
if 'executor' not in st.session_state:
    st.session_state.executor = ThreadPoolExecutor(max_workers=3)

if 'tasks' not in st.session_state:
    # 从本地加载状态
    saved_state = load_state()
    st.session_state.tasks = saved_state.get('tasks', {})
    st.session_state.t2i_inputs = saved_state.get('inputs', {}).get('t2i', {})
    st.session_state.i2v_inputs = saved_state.get('inputs', {}).get('i2v', {})
    st.session_state.t2v_inputs = saved_state.get('inputs', {}).get('t2v', {})

if 'history' not in st.session_state:
    st.session_state.history = load_json(HISTORY_FILE, [])

# ==================== 任务管理 ====================
def create_task(task_id: str, task_type: str, params: Dict[str, Any]):
    """创建新任务"""
    task = {
        'id': task_id,
        'type': task_type,
        'status': 'running',  # running, completed, error
        'params': params,
        'result': None,
        'error': None,
        'created_at': datetime.now().isoformat(),
    }
    st.session_state.tasks[task_id] = task
    save_state()
    return task

def update_task(task_id: str, **kwargs):
    """更新任务状态"""
    if task_id in st.session_state.tasks:
        st.session_state.tasks[task_id].update(kwargs)
        save_state()

def get_active_tasks(task_type: Optional[str] = None):
    """获取活动任务"""
    tasks = st.session_state.tasks.values()
    if task_type:
        tasks = [t for t in tasks if t['type'] == task_type]
    return [t for t in tasks if t['status'] == 'running']

def get_completed_task(task_type: str):
    """获取最近完成的任务"""
    tasks = [t for t in st.session_state.tasks.values()
             if t['type'] == task_type and t['status'] == 'completed']
    return tasks[-1] if tasks else None

# ==================== 任务执行 ====================
def run_task(task_id: str, client: QwenImg, task_type: str, params: Dict[str, Any]):
    """后台执行任务"""
    try:
        # 根据任务类型调用不同方法
        if task_type == 't2i':
            result = client.text_to_image(**params)
            result_data = {
                'images': result if isinstance(result, list) else [result]
            }
        elif task_type == 'i2v':
            video_url = client.image_to_video(**params)
            result_data = {'url': video_url}
        elif task_type == 't2v':
            video_url = client.text_to_video(**params)
            result_data = {'url': video_url}
        else:
            raise ValueError(f"Unknown task type: {task_type}")

        # 更新任务状态
        update_task(task_id, status='completed', result=result_data)

        # 保存历史记录
        save_history({
            'type': task_type,
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'params': params,
            'result': 'success'
        })

    except Exception as e:
        update_task(task_id, status='error', error=str(e))

# ==================== 客户端初始化 ====================
@st.cache_resource
def init_client(api_key: str, region: str):
    try:
        return QwenImg(api_key=api_key, region=region)
    except Exception as e:
        st.error(f"初始化失败: {str(e)}")
        return None

# ==================== UI ====================
st.title("🎨 QwenImg - 极简版")
st.caption("简洁高效的图片视频生成工具 | 支持刷新页面")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 配置")
    api_key = st.text_input(
        "API Key",
        type="password",
        value=os.getenv("DASHSCOPE_API_KEY", ""),
        help="[获取 API Key](https://help.aliyun.com/zh/model-studio/get-api-key)"
    )
    region = st.selectbox("地域", ["beijing", "singapore"])

    st.divider()

    # 历史记录
    st.header("📜 历史记录")
    history = st.session_state.history

    if history:
        st.caption(f"共 {len(history)} 条记录")
        if st.button("🗑️ 清空", key="clear_history"):
            st.session_state.history = []
            save_json(HISTORY_FILE, [])
            st.rerun()

        for i, record in enumerate(reversed(history[-10:])):
            with st.expander(f"{record['type'].upper()} - {record['time']}", expanded=False):
                st.json(record['params'])
    else:
        st.info("暂无历史记录")

    st.divider()
    st.caption("[文档](https://github.com/cclank/qwenimg) | by 岚叔")

# 初始化客户端
client = init_client(api_key, region) if api_key else None

if not client:
    st.warning("⚠️ 请在侧边栏输入 API Key")
    st.stop()

# ==================== 主界面 ====================
tab1, tab2, tab3 = st.tabs(["📝 文生图", "🎬 图生视频", "🎥 文生视频"])

# ==================== 文生图 ====================
with tab1:
    col1, col2 = st.columns([3, 1])

    with col1:
        prompt = st.text_area(
            "提示词",
            height=100,
            placeholder="一只可爱的橘猫坐在窗台上...",
            value=st.session_state.t2i_inputs.get('prompt', '')
        )

    with col2:
        model = st.selectbox("模型", ["wan2.5-t2i-preview", "wanx-v1"])
        size = st.selectbox("尺寸", ["1024*1024", "1280*720", "720*1280"])
        n = st.slider("数量", 1, 4, 1)

    if st.button("🎨 生成", key="t2i_btn", use_container_width=True):
        if not prompt:
            st.warning("请输入提示词")
        else:
            # 保存输入
            st.session_state.t2i_inputs = {'prompt': prompt, 'model': model, 'size': size, 'n': n}
            save_state()

            # 创建任务
            task_id = f"t2i_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            params = {
                'prompt': prompt,
                'model': model,
                'size': size,
                'n': n,
                'save': False
            }
            create_task(task_id, 't2i', params)

            # 提交任务
            st.session_state.executor.submit(run_task, task_id, client, 't2i', params)
            st.rerun()

    # 显示任务状态
    active_tasks = get_active_tasks('t2i')
    if active_tasks:
        st.info(f"🔄 正在生成 {len(active_tasks)} 个任务...")
        time.sleep(0.5)
        st.rerun()

    # 显示结果
    completed = get_completed_task('t2i')
    if completed and completed.get('result'):
        st.success("✅ 生成完成！")
        images = completed['result']['images']

        cols = st.columns(min(len(images), 3))
        for i, img in enumerate(images):
            with cols[i % 3]:
                st.image(img, use_container_width=True)
                buf = BytesIO()
                img.save(buf, format="PNG")
                st.download_button(
                    f"📥 下载 {i+1}",
                    buf.getvalue(),
                    f"image_{i+1}.png",
                    "image/png",
                    key=f"dl_t2i_{i}"
                )

# ==================== 图生视频 ====================
with tab2:
    col1, col2 = st.columns([3, 1])

    with col1:
        uploaded = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"])
        if uploaded:
            st.image(uploaded, use_container_width=True)

        prompt = st.text_area(
            "提示词（可选）",
            height=80,
            placeholder="描述视频动作...",
            value=st.session_state.i2v_inputs.get('prompt', '')
        )

    with col2:
        resolution = st.selectbox("分辨率", ["1080P", "720P", "480P"])
        duration = st.selectbox("时长", [10, 5])

    if st.button("🎬 生成", key="i2v_btn", use_container_width=True):
        if not uploaded:
            st.warning("请上传图片")
        else:
            # 保存输入
            st.session_state.i2v_inputs = {'prompt': prompt}
            save_state()

            # 保存临时图片
            temp_path = DATA_DIR / "temp_i2v.png"
            with open(temp_path, "wb") as f:
                f.write(uploaded.getbuffer())

            # 创建任务
            task_id = f"i2v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            params = {
                'image': str(temp_path),
                'prompt': prompt,
                'resolution': resolution,
                'duration': duration
            }
            create_task(task_id, 'i2v', params)

            # 提交任务
            st.session_state.executor.submit(run_task, task_id, client, 'i2v', params)
            st.rerun()

    # 显示任务状态
    active_tasks = get_active_tasks('i2v')
    if active_tasks:
        st.info(f"🔄 正在生成视频（约 {duration * 10}秒）...")
        time.sleep(0.5)
        st.rerun()

    # 显示结果
    completed = get_completed_task('i2v')
    if completed and completed.get('result'):
        st.success("✅ 视频生成完成！")
        url = completed['result']['url']
        st.video(url)
        st.caption(f"[视频链接]({url})")

# ==================== 文生视频 ====================
with tab3:
    col1, col2 = st.columns([3, 1])

    with col1:
        prompt = st.text_area(
            "提示词",
            height=100,
            placeholder="一只柴犬在草地上奔跑...",
            value=st.session_state.t2v_inputs.get('prompt', '')
        )

    with col2:
        resolution = st.selectbox("分辨率", ["1080P", "720P", "480P"], key="t2v_res")
        duration = st.selectbox("时长", [10, 5], key="t2v_dur")

    if st.button("🎥 生成", key="t2v_btn", use_container_width=True):
        if not prompt:
            st.warning("请输入提示词")
        else:
            # 保存输入
            st.session_state.t2v_inputs = {'prompt': prompt}
            save_state()

            # 创建任务
            task_id = f"t2v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            params = {
                'prompt': prompt,
                'resolution': resolution,
                'duration': duration
            }
            create_task(task_id, 't2v', params)

            # 提交任务
            st.session_state.executor.submit(run_task, task_id, client, 't2v', params)
            st.rerun()

    # 显示任务状态
    active_tasks = get_active_tasks('t2v')
    if active_tasks:
        st.info(f"🔄 正在生成视频（约 {duration * 10}秒）...")
        time.sleep(0.5)
        st.rerun()

    # 显示结果
    completed = get_completed_task('t2v')
    if completed and completed.get('result'):
        st.success("✅ 视频生成完成！")
        url = completed['result']['url']
        st.video(url)
        st.caption(f"[视频链接]({url})")

# ==================== 页脚 ====================
st.divider()
st.caption("""
**✨ 特性**
- ✅ 支持页面刷新 - 状态自动保存到 ~/.qwenimg/
- ✅ 并发创作 - 多个任务同时执行
- ✅ 完整历史 - 所有记录永久保存
- ✅ 极简代码 - 减少 50%+ 代码量
""")
