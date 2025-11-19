"""数据库模型定义"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float
from sqlalchemy.sql import func
from .database import Base


class GenerationTask(Base):
    """生成任务模型"""
    __tablename__ = "generation_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    task_type = Column(String(20), nullable=False)  # text_to_image, image_to_video, text_to_video
    status = Column(String(20), default="pending")  # pending, running, completed, failed

    # 输入参数
    prompt = Column(Text)
    negative_prompt = Column(Text, nullable=True)
    model = Column(String(50), nullable=True)

    # 文生图参数
    image_count = Column(Integer, nullable=True)
    image_size = Column(String(20), nullable=True)

    # 视频参数
    resolution = Column(String(10), nullable=True)
    duration = Column(Integer, nullable=True)

    # 图生视频参数
    input_image_url = Column(Text, nullable=True)
    audio_url = Column(Text, nullable=True)

    # 额外参数
    seed = Column(Integer, nullable=True)
    watermark = Column(Integer, default=0)
    params = Column(JSON, nullable=True)  # 其他参数JSON存储

    # 结果
    result_urls = Column(JSON, nullable=True)  # 结果URL列表
    error_message = Column(Text, nullable=True)

    # 元数据
    progress = Column(Float, default=0.0)  # 进度 0-100
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # 用户信息（未来扩展）
    user_id = Column(String(50), nullable=True, index=True)
    session_id = Column(String(100), nullable=True, index=True)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status,
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "model": self.model,
            "image_count": self.image_count,
            "image_size": self.image_size,
            "resolution": self.resolution,
            "duration": self.duration,
            "input_image_url": self.input_image_url,
            "audio_url": self.audio_url,
            "seed": self.seed,
            "watermark": bool(self.watermark),
            "params": self.params,
            "result_urls": self.result_urls,
            "error_message": self.error_message,
            "progress": self.progress,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "user_id": self.user_id,
            "session_id": self.session_id,
        }


class Inspiration(Base):
    """灵感示例模型 - 用于激发用户创作"""
    __tablename__ = "inspirations"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), index=True)  # 分类：风景、人物、动物、科幻等
    title = Column(String(200), nullable=False)
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    thumbnail_url = Column(Text, nullable=True)
    task_type = Column(String(20), nullable=False)  # text_to_image, text_to_video等
    tags = Column(JSON, nullable=True)  # 标签列表
    likes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "category": self.category,
            "title": self.title,
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "thumbnail_url": self.thumbnail_url,
            "task_type": self.task_type,
            "tags": self.tags,
            "likes": self.likes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
