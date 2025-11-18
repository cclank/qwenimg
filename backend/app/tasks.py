"""异步任务管理系统 - 支持并发创作"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional, Callable, Any
from concurrent.futures import ThreadPoolExecutor
import sys
import os
from PIL import Image
import io
import base64

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
            try:
                # 关闭WebSocket连接
                websocket = self.active_connections[session_id]
                if hasattr(websocket, 'close'):
                    websocket.close()
            except Exception as e:
                logger.error(f"Failed to close WebSocket for {session_id}: {e}")
            finally:
                # 从活动连接中移除
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
                    message = {
                        "type": "progress",
                        "task_id": task_id,
                        "data": {
                            "progress": progress,
                            "status": status
                        }
                    }
                    print(f"Sending progress update: {message}")  # 调试信息
                    await manager.send_message(task.session_id, message)
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
                    print(f"Sending task completion: {message}")  # 调试信息
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
            # 确保outputs目录存在
            output_dir = "./outputs"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            if isinstance(result, list):
                # 多张图片
                for i, img in enumerate(result):
                    # 保存图片到本地
                    if isinstance(img, Image.Image):
                        filename = f"{task_id}_{i}.png"
                        filepath = os.path.join(output_dir, filename)
                        img.save(filepath)
                        result_urls.append(f"/outputs/{filename}")
                    else:
                        # 如果不是PIL图像，假设是base64编码
                        filename = f"{task_id}_{i}.png"
                        filepath = os.path.join(output_dir, filename)
                        # 解码base64并保存
                        with open(filepath, "wb") as f:
                            f.write(base64.b64decode(img))
                        result_urls.append(f"/outputs/{filename}")
            else:
                # 单张图片
                filename = f"{task_id}_0.png"
                filepath = os.path.join(output_dir, filename)
                if isinstance(result, Image.Image):
                    result.save(filepath)
                else:
                    # 如果不是PIL图像，假设是base64编码
                    with open(filepath, "wb") as f:
                        f.write(base64.b64decode(result))
                result_urls.append(f"/outputs/{filename}")

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

            result = await loop.run_in_executor(
                executor,
                self._image_to_video_sync,
                params
            )

            await self.update_task_progress(task_id, 60.0, "running")

            # 确保outputs目录存在
            output_dir = "./outputs"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # 保存视频到本地并返回URL
            filename = f"{task_id}.mp4"
            filepath = os.path.join(output_dir, filename)

            # 如果result是URL，下载视频内容
            if isinstance(result, str) and (result.startswith("http://") or result.startswith("https://")):
                logger.info(f"Video URL received: {result}")
                await self.update_task_progress(task_id, 70.0, "running")

                # 在线程池中下载（避免阻塞事件循环）
                await loop.run_in_executor(
                    executor,
                    self._download_video,
                    result,
                    filepath
                )

                await self.update_task_progress(task_id, 95.0, "running")
            # 如果result是文件路径，复制文件
            elif isinstance(result, str) and os.path.exists(result):
                import shutil
                shutil.copy(result, filepath)
                logger.info(f"Copied video file from {result} to {filepath}")
            # 如果result是base64编码，解码保存
            elif isinstance(result, str):
                # 检查是否是base64数据URI
                if result.startswith("data:video"):
                    # 提取base64部分
                    base64_data = result.split(",")[1]
                    with open(filepath, "wb") as f:
                        f.write(base64.b64decode(base64_data))
                else:
                    # 直接是base64编码
                    with open(filepath, "wb") as f:
                        f.write(base64.b64decode(result))
                logger.info(f"Saved base64 video to {filepath}")
            else:
                raise ValueError(f"Unexpected result format: {type(result)}")

            result_url = f"/outputs/{filename}"
            logger.info(f"Video saved successfully: {result_url}")
            await self.complete_task(task_id, [result_url])

        except Exception as e:
            logger.error(f"Image to video task failed: {e}", exc_info=True)
            await self.complete_task(task_id, [], str(e))

    def _image_to_video_sync(self, params: dict):
        """同步执行图生视频"""
        # 转换图片URL路径为文件系统路径
        image_url = params.get("image_url", "")
        if image_url.startswith("/uploads/"):
            # 将 /uploads/xxx.png 转换为 ./uploads/xxx.png
            image_path = "." + image_url
            logger.info(f"Converting image URL {image_url} to file path {image_path}")
        elif image_url.startswith("http://") or image_url.startswith("https://"):
            # 如果是完整URL，直接使用
            image_path = image_url
        else:
            # 默认作为文件路径处理
            image_path = image_url

        # 验证文件是否存在（如果是本地文件）
        if not (image_path.startswith("http://") or image_path.startswith("https://")):
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")

        return self.qwen_client.image_to_video(
            image=image_path,
            prompt=params.get("prompt"),
            negative_prompt=params.get("negative_prompt"),
            resolution=params.get("resolution", "1080P"),
            duration=params.get("duration", 10),
            audio=params.get("audio_url"),
            seed=params.get("seed"),
            watermark=params.get("watermark", False)
        )

    def _download_video(self, url: str, filepath: str) -> None:
        """下载视频文件（使用流式下载）"""
        import requests

        logger.info(f"Starting video download from: {url}")

        # 使用流式下载，超时时间设置为(连接超时, 读取超时)
        response = requests.get(url, stream=True, timeout=(10, 300))
        response.raise_for_status()

        # 检查Content-Type
        content_type = response.headers.get('Content-Type', '')
        logger.info(f"Content-Type: {content_type}")

        # 获取文件大小
        total_size = int(response.headers.get('content-length', 0))
        logger.info(f"Total size: {total_size} bytes ({total_size / 1024 / 1024:.2f} MB)")

        # 流式下载，分块写入文件
        downloaded_size = 0
        chunk_size = 8192  # 8KB per chunk

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)

                    # 每下载10MB打印一次进度
                    if downloaded_size % (10 * 1024 * 1024) < chunk_size:
                        logger.info(f"Downloaded {downloaded_size / 1024 / 1024:.2f} MB...")

        # 验证下载是否完整
        actual_size = os.path.getsize(filepath)
        logger.info(f"Download completed. File size: {actual_size} bytes ({actual_size / 1024 / 1024:.2f} MB)")

        if total_size > 0 and actual_size < total_size:
            raise ValueError(f"Download incomplete: expected {total_size} bytes, got {actual_size} bytes")

        if actual_size < 1000:  # 小于1KB可能是错误页面
            raise ValueError(f"Downloaded file too small ({actual_size} bytes), likely an error response")

    async def run_text_to_video(self, task_id: str, params: dict):
        """执行文生视频任务"""
        try:
            self.init_client()
            await self.update_task_progress(task_id, 10.0, "running")

            loop = asyncio.get_event_loop()
            await self.update_task_progress(task_id, 30.0, "running")

            result = await loop.run_in_executor(
                executor,
                self._text_to_video_sync,
                params
            )

            await self.update_task_progress(task_id, 60.0, "running")

            # 确保outputs目录存在
            output_dir = "./outputs"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # 保存视频到本地并返回URL
            filename = f"{task_id}.mp4"
            filepath = os.path.join(output_dir, filename)

            # 处理不同的返回格式
            if result is None:
                raise ValueError("Text to video task returned None")

            # 如果result是URL，下载视频内容
            if isinstance(result, str) and (result.startswith("http://") or result.startswith("https://")):
                logger.info(f"Video URL received: {result}")
                await self.update_task_progress(task_id, 70.0, "running")

                # 在线程池中下载（避免阻塞事件循环）
                await loop.run_in_executor(
                    executor,
                    self._download_video,
                    result,
                    filepath
                )

                await self.update_task_progress(task_id, 95.0, "running")
            # 如果result是文件路径，复制文件
            elif isinstance(result, str) and os.path.exists(result):
                import shutil
                shutil.copy(result, filepath)
                logger.info(f"Copied video file from {result} to {filepath}")
            # 如果result是base64编码，解码保存
            elif isinstance(result, str):
                # 检查是否是base64数据URI
                if result.startswith("data:video"):
                    # 提取base64部分
                    base64_data = result.split(",")[1]
                    with open(filepath, "wb") as f:
                        f.write(base64.b64decode(base64_data))
                else:
                    # 直接是base64编码
                    with open(filepath, "wb") as f:
                        f.write(base64.b64decode(result))
                logger.info(f"Saved base64 video to {filepath}")
            else:
                # 如果是字典格式，提取视频数据
                if isinstance(result, dict) and "video" in result:
                    video_data = result["video"]
                    if isinstance(video_data, str):
                        # 检查是否是URL
                        if video_data.startswith("http://") or video_data.startswith("https://"):
                            logger.info(f"Video URL in dict format: {video_data}")
                            await self.update_task_progress(task_id, 70.0, "running")

                            # 使用统一的下载函数
                            await loop.run_in_executor(
                                executor,
                                self._download_video,
                                video_data,
                                filepath
                            )

                            await self.update_task_progress(task_id, 95.0, "running")
                        # 检查是否是base64数据URI
                        elif video_data.startswith("data:video"):
                            base64_data = video_data.split(",")[1]
                            with open(filepath, "wb") as f:
                                f.write(base64.b64decode(base64_data))
                        else:
                            with open(filepath, "wb") as f:
                                f.write(base64.b64decode(video_data))
                        logger.info(f"Saved dict video to {filepath}")
                    else:
                        raise ValueError(f"Unexpected video data type: {type(video_data)}")
                else:
                    raise ValueError(f"Unexpected result format: {type(result)}")

            result_url = f"/outputs/{filename}"
            logger.info(f"Video saved successfully: {result_url}")
            await self.complete_task(task_id, [result_url])

        except Exception as e:
            logger.error(f"Text to video task failed: {e}", exc_info=True)
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
