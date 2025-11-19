"""文件上传API路由"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Dict
import os
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["upload"])

# 确保上传目录存在
UPLOAD_DIR = "./uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 允许的图片格式
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(filename)[1].lower()


@router.post("/image", response_model=Dict[str, str])
async def upload_image(file: UploadFile = File(...)):
    """
    上传图片文件

    返回:
        {"url": "上传后的图片URL"}
    """
    try:
        # 验证文件类型
        file_ext = get_file_extension(file.filename)
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式。允许的格式: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # 读取文件内容
        contents = await file.read()

        # 验证文件大小
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件太大。最大允许大小: {MAX_FILE_SIZE / 1024 / 1024}MB"
            )

        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        new_filename = f"{timestamp}_{unique_id}{file_ext}"

        # 保存文件
        file_path = os.path.join(UPLOAD_DIR, new_filename)
        with open(file_path, "wb") as f:
            f.write(contents)

        # 返回URL（相对路径）
        file_url = f"/uploads/{new_filename}"

        logger.info(f"Image uploaded successfully: {file_url}")

        return {"url": file_url}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")
