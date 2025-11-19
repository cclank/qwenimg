"""Pydantic 模式定义 - 用于API请求和响应验证"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ========== 请求模型 ==========

class TextToImageRequest(BaseModel):
    """文生图请求"""
    prompt: str = Field(..., description="图片描述提示词")
    negative_prompt: Optional[str] = Field(None, description="负面提示词")
    model: Optional[str] = Field("wan2.5-t2i-preview", description="模型名称")
    n: Optional[int] = Field(1, ge=1, le=4, description="生成数量")
    size: Optional[str] = Field("1024*1024", description="图片尺寸")
    seed: Optional[int] = Field(None, description="随机种子")
    watermark: Optional[bool] = Field(False, description="是否添加水印")
    session_id: Optional[str] = Field(None, description="会话ID")


class ImageToVideoRequest(BaseModel):
    """图生视频请求"""
    image_url: str = Field(..., description="输入图片URL或Base64")
    prompt: Optional[str] = Field(None, description="视频动作描述")
    negative_prompt: Optional[str] = Field(None, description="负面提示词")
    model: Optional[str] = Field("wan2.5-i2v-preview", description="模型名称")
    resolution: Optional[str] = Field("1080P", description="分辨率")
    duration: Optional[int] = Field(10, description="时长（秒）")
    audio_url: Optional[str] = Field(None, description="音频URL")
    seed: Optional[int] = Field(None, description="随机种子")
    watermark: Optional[bool] = Field(False, description="是否添加水印")
    session_id: Optional[str] = Field(None, description="会话ID")


class TextToVideoRequest(BaseModel):
    """文生视频请求"""
    prompt: str = Field(..., description="视频场景描述")
    negative_prompt: Optional[str] = Field(None, description="负面提示词")
    model: Optional[str] = Field("wan2.5-t2v-preview", description="模型名称")
    resolution: Optional[str] = Field("1080P", description="分辨率")
    duration: Optional[int] = Field(10, description="时长（秒）")
    seed: Optional[int] = Field(None, description="随机种子")
    watermark: Optional[bool] = Field(False, description="是否添加水印")
    session_id: Optional[str] = Field(None, description="会话ID")


# ========== 响应模型 ==========

class TaskResponse(BaseModel):
    """任务创建响应"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    message: str = Field(..., description="提示信息")


class TaskStatus(BaseModel):
    """任务状态"""
    task_id: str
    task_type: str
    status: str  # pending, running, completed, failed
    progress: float = Field(0.0, ge=0.0, le=100.0)
    prompt: Optional[str] = None
    result_urls: Optional[List[str]] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """任务列表响应"""
    tasks: List[TaskStatus]
    total: int
    page: int = 1
    page_size: int = 20


class InspirationBase(BaseModel):
    """灵感基础模型"""
    category: str
    title: str
    prompt: str
    negative_prompt: Optional[str] = None
    thumbnail_url: Optional[str] = None
    task_type: str
    tags: Optional[List[str]] = None


class InspirationCreate(InspirationBase):
    """创建灵感"""
    pass


class InspirationResponse(InspirationBase):
    """灵感响应"""
    id: int
    likes: int
    created_at: datetime

    class Config:
        from_attributes = True


class InspirationListResponse(BaseModel):
    """灵感列表响应"""
    inspirations: List[InspirationResponse]
    total: int
    categories: List[str]


# ========== WebSocket 消息模型 ==========

class WSMessage(BaseModel):
    """WebSocket消息"""
    type: str  # task_update, task_completed, task_failed, progress
    task_id: str
    data: Dict[str, Any]


class WSTaskUpdate(BaseModel):
    """任务更新消息"""
    task_id: str
    status: str
    progress: float
    message: Optional[str] = None


class WSTaskCompleted(BaseModel):
    """任务完成消息"""
    task_id: str
    result_urls: List[str]
    task_type: str


class WSTaskFailed(BaseModel):
    """任务失败消息"""
    task_id: str
    error_message: str
