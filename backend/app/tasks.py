"""异步任务管理系统 - 支持并发创作"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional, Callable, Any
from concurrent.futures import ThreadPoolExecutor
import sys
import os

# 添加父目录到路径以导入qwenimg
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from qwenimg import QwenImg
from .database import SessionLocal
from .models import GenerationTask
import logging

logger = logging.getLogger(__name__)

# 线程池执行器 - 用于运行同步的QwenImg调用
executor = ThreadPoolExecutor(max_workers=5)

# WebSocket连接管理器
class ConnectionManager:
    """WebSocket连接管理"""
    def __init__(self):
        self.active_connections: Dict[str, Any] = {}  # session_id -> websocket

    async def connect(self, websocket: Any, session_id: str):
        """连接WebSocket"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected: {session_id}")

    def disconnect(self, session_id: str):
        """断开连接"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected: {session_id}")

    async def send_message(self, session_id: str, message: dict):
        """发送消息到指定会话"""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to {session_id}: {e}")
                self.disconnect(session_id)

    async def broadcast(self, message: dict):
        """广播消息到所有连接"""
        for session_id in list(self.active_connections.keys()):
            await self.send_message(session_id, message)


# 全局连接管理器
manager = ConnectionManager()


class TaskManager:
    """任务管理器"""
    def __init__(self):
        self.tasks: Dict[str, asyncio.Task] = {}  # task_id -> asyncio.Task
        self.qwen_client: Optional[QwenImg] = None

    def init_client(self, api_key: Optional[str] = None):
        """初始化QwenImg客户端"""
        if not self.qwen_client:
            self.qwen_client = QwenImg(api_key=api_key)
            logger.info("QwenImg client initialized")

    async def update_task_progress(self, task_id: str, progress: float, status: str = "running"):
        """更新任务进度"""
        db = SessionLocal()
        try:
            task = db.query(GenerationTask).filter(GenerationTask.task_id == task_id).first()
            if task:
                task.progress = progress
                task.status = status
                task.updated_at = datetime.now()
                db.commit()

                # 通过WebSocket发送进度更新
                if task.session_id:
                    await manager.send_message(task.session_id, {
                        "type": "progress",
                        "task_id": task_id,
                        "data": {
                            "progress": progress,
                            "status": status
                        }
                    })
        except Exception as e:
            logger.error(f"Failed to update task progress: {e}")
        finally:
            db.close()

    async def complete_task(self, task_id: str, result_urls: list, error_message: Optional[str] = None):
        """完成任务"""
        db = SessionLocal()
        try:
            task = db.query(GenerationTask).filter(GenerationTask.task_id == task_id).first()
            if task:
                task.status = "completed" if not error_message else "failed"
                task.result_urls = result_urls if not error_message else None
                task.error_message = error_message
                task.progress = 100.0 if not error_message else task.progress
                task.completed_at = datetime.now()
                db.commit()

                # 通过WebSocket发送完成消息
                if task.session_id:
                    message = {
                        "type": "task_completed" if not error_message else "task_failed",
                        "task_id": task_id,
                        "data": {
                            "result_urls": result_urls,
                            "task_type": task.task_type,
                            "error_message": error_message
                        } if not error_message else {
                            "error_message": error_message
                        }
                    }
                    await manager.send_message(task.session_id, message)
        except Exception as e:
            logger.error(f"Failed to complete task: {e}")
        finally:
            db.close()

    async def run_text_to_image(self, task_id: str, params: dict):
        """执行文生图任务"""
        try:
            self.init_client()
            await self.update_task_progress(task_id, 10.0, "running")

            # 在线程池中运行同步调用
            loop = asyncio.get_event_loop()
            await self.update_task_progress(task_id, 30.0, "running")

            result = await loop.run_in_executor(
                executor,
                self._text_to_image_sync,
                params
            )

            await self.update_task_progress(task_id, 90.0, "running")

            # 处理结果（URL列表）
            result_urls = []
            if isinstance(result, list):
                # 多张图片
                for i, img in enumerate(result):
                    # TODO: 将图片上传到云存储或保存到本地，返回URL
                    # 这里暂时使用占位符
                    result_urls.append(f"/api/results/{task_id}_{i}.png")
            else:
                # 单张图片
                result_urls.append(f"/api/results/{task_id}_0.png")

            await self.complete_task(task_id, result_urls)

        except Exception as e:
            logger.error(f"Text to image task failed: {e}")
            await self.complete_task(task_id, [], str(e))

    def _text_to_image_sync(self, params: dict):
        """同步执行文生图"""
        return self.qwen_client.text_to_image(
            prompt=params.get("prompt"),
            negative_prompt=params.get("negative_prompt"),
            model=params.get("model", "wan2.5-t2i-preview"),
            n=params.get("n", 1),
            size=params.get("size", "1024*1024"),
            seed=params.get("seed"),
            watermark=params.get("watermark", False),
            save=True,  # 保存到本地
            return_pil=True
        )

    async def run_image_to_video(self, task_id: str, params: dict):
        """执行图生视频任务"""
        try:
            self.init_client()
            await self.update_task_progress(task_id, 10.0, "running")

            loop = asyncio.get_event_loop()
            await self.update_task_progress(task_id, 30.0, "running")

            result_url = await loop.run_in_executor(
                executor,
                self._image_to_video_sync,
                params
            )

            await self.update_task_progress(task_id, 90.0, "running")
            await self.complete_task(task_id, [result_url])

        except Exception as e:
            logger.error(f"Image to video task failed: {e}")
            await self.complete_task(task_id, [], str(e))

    def _image_to_video_sync(self, params: dict):
        """同步执行图生视频"""
        return self.qwen_client.image_to_video(
            image=params.get("image_url"),
            prompt=params.get("prompt"),
            negative_prompt=params.get("negative_prompt"),
            resolution=params.get("resolution", "1080P"),
            duration=params.get("duration", 10),
            audio=params.get("audio_url"),
            seed=params.get("seed"),
            watermark=params.get("watermark", False)
        )

    async def run_text_to_video(self, task_id: str, params: dict):
        """执行文生视频任务"""
        try:
            self.init_client()
            await self.update_task_progress(task_id, 10.0, "running")

            loop = asyncio.get_event_loop()
            await self.update_task_progress(task_id, 30.0, "running")

            result_url = await loop.run_in_executor(
                executor,
                self._text_to_video_sync,
                params
            )

            await self.update_task_progress(task_id, 90.0, "running")
            await self.complete_task(task_id, [result_url])

        except Exception as e:
            logger.error(f"Text to video task failed: {e}")
            await self.complete_task(task_id, [], str(e))

    def _text_to_video_sync(self, params: dict):
        """同步执行文生视频"""
        return self.qwen_client.text_to_video(
            prompt=params.get("prompt"),
            negative_prompt=params.get("negative_prompt"),
            model=params.get("model", "wan2.5-t2v-preview"),
            resolution=params.get("resolution", "1080P"),
            duration=params.get("duration", 10),
            seed=params.get("seed"),
            watermark=params.get("watermark", False)
        )

    async def create_task(self, task_type: str, params: dict, session_id: Optional[str] = None) -> str:
        """创建并启动任务"""
        task_id = str(uuid.uuid4())

        # 保存到数据库
        db = SessionLocal()
        try:
            db_task = GenerationTask(
                task_id=task_id,
                task_type=task_type,
                status="pending",
                prompt=params.get("prompt"),
                negative_prompt=params.get("negative_prompt"),
                model=params.get("model"),
                image_count=params.get("n"),
                image_size=params.get("size"),
                resolution=params.get("resolution"),
                duration=params.get("duration"),
                input_image_url=params.get("image_url"),
                audio_url=params.get("audio_url"),
                seed=params.get("seed"),
                watermark=1 if params.get("watermark") else 0,
                params=params,
                session_id=session_id
            )
            db.add(db_task)
            db.commit()
        finally:
            db.close()

        # 启动异步任务
        if task_type == "text_to_image":
            task = asyncio.create_task(self.run_text_to_image(task_id, params))
        elif task_type == "image_to_video":
            task = asyncio.create_task(self.run_image_to_video(task_id, params))
        elif task_type == "text_to_video":
            task = asyncio.create_task(self.run_text_to_video(task_id, params))
        else:
            raise ValueError(f"Unknown task type: {task_type}")

        self.tasks[task_id] = task
        logger.info(f"Task created: {task_id} ({task_type})")

        return task_id

    def get_task_status(self, task_id: str) -> Optional[dict]:
        """获取任务状态"""
        db = SessionLocal()
        try:
            task = db.query(GenerationTask).filter(GenerationTask.task_id == task_id).first()
            if task:
                return task.to_dict()
            return None
        finally:
            db.close()


# 全局任务管理器实例
task_manager = TaskManager()
