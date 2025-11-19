"""生成任务API路由"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..schemas import (
    TextToImageRequest,
    ImageToVideoRequest,
    TextToVideoRequest,
    TaskResponse,
    TaskStatus,
    TaskListResponse
)
from ..models import GenerationTask
from ..tasks import task_manager

router = APIRouter(prefix="/api/generation", tags=["generation"])


@router.post("/text-to-image", response_model=TaskResponse)
async def create_text_to_image_task(request: TextToImageRequest):
    """创建文生图任务"""
    try:
        params = {
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt,
            "model": request.model,
            "n": request.n,
            "size": request.size,
            "seed": request.seed,
            "watermark": request.watermark,
        }

        task_id = await task_manager.create_task(
            task_type="text_to_image",
            params=params,
            session_id=request.session_id
        )

        return TaskResponse(
            task_id=task_id,
            status="pending",
            message="文生图任务已创建，正在处理中..."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image-to-video", response_model=TaskResponse)
async def create_image_to_video_task(request: ImageToVideoRequest):
    """创建图生视频任务"""
    try:
        params = {
            "image_url": request.image_url,
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt,
            "model": request.model,
            "resolution": request.resolution,
            "duration": request.duration,
            "audio_url": request.audio_url,
            "seed": request.seed,
            "watermark": request.watermark,
        }

        task_id = await task_manager.create_task(
            task_type="image_to_video",
            params=params,
            session_id=request.session_id
        )

        return TaskResponse(
            task_id=task_id,
            status="pending",
            message="图生视频任务已创建，正在处理中..."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text-to-video", response_model=TaskResponse)
async def create_text_to_video_task(request: TextToVideoRequest):
    """创建文生视频任务"""
    try:
        params = {
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt,
            "model": request.model,
            "resolution": request.resolution,
            "duration": request.duration,
            "seed": request.seed,
            "watermark": request.watermark,
        }

        task_id = await task_manager.create_task(
            task_type="text_to_video",
            params=params,
            session_id=request.session_id
        )

        return TaskResponse(
            task_id=task_id,
            status="pending",
            message="文生视频任务已创建，正在处理中..."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str, db: Session = Depends(get_db)):
    """获取任务状态"""
    task = db.query(GenerationTask).filter(GenerationTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return TaskStatus(
        task_id=task.task_id,
        task_type=task.task_type,
        status=task.status,
        progress=task.progress,
        prompt=task.prompt,
        result_urls=task.result_urls,
        error_message=task.error_message,
        created_at=task.created_at,
        completed_at=task.completed_at
    )


@router.get("/tasks", response_model=TaskListResponse)
async def get_tasks(
    page: int = 1,
    page_size: int = 20,
    status: str = None,
    task_type: str = None,
    session_id: str = None,
    db: Session = Depends(get_db)
):
    """获取任务列表"""
    query = db.query(GenerationTask)

    # 过滤条件
    if status:
        query = query.filter(GenerationTask.status == status)
    if task_type:
        query = query.filter(GenerationTask.task_type == task_type)
    if session_id:
        query = query.filter(GenerationTask.session_id == session_id)

    # 分页
    total = query.count()
    tasks = query.order_by(GenerationTask.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    task_list = [
        TaskStatus(
            task_id=task.task_id,
            task_type=task.task_type,
            status=task.status,
            progress=task.progress,
            prompt=task.prompt,
            result_urls=task.result_urls,
            error_message=task.error_message,
            created_at=task.created_at,
            completed_at=task.completed_at
        )
        for task in tasks
    ]

    return TaskListResponse(
        tasks=task_list,
        total=total,
        page=page,
        page_size=page_size
    )


@router.delete("/task/{task_id}")
async def delete_task(task_id: str, url: str = None, db: Session = Depends(get_db)):
    """删除任务或任务中的特定图片"""
    task = db.query(GenerationTask).filter(GenerationTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 如果指定了URL，则只删除该图片
    if url:
        if task.result_urls and url in task.result_urls:
            # 创建新的列表以触发SQLAlchemy更新
            new_urls = [u for u in task.result_urls if u != url]
            task.result_urls = new_urls
            
            # 如果没有剩余图片，则删除整个任务
            if not new_urls:
                db.delete(task)
                db.commit()
                return {"message": "任务已删除"}
            
            # 否则只更新result_urls
            # 注意：对于JSON类型，需要显式标记修改或重新赋值
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(task, "result_urls")
            db.commit()
            return {"message": "图片已删除"}
        else:
            return {"message": "图片不存在或已删除"}

    # 如果没有指定URL，删除整个任务
    db.delete(task)
    db.commit()

    return {"message": "任务已删除"}


@router.delete("/tasks")
async def clear_tasks(session_id: str, db: Session = Depends(get_db)):
    """清空指定会话的所有任务"""
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")

    # 查询该会话的所有任务
    tasks = db.query(GenerationTask).filter(GenerationTask.session_id == session_id).all()
    
    if not tasks:
        return {"message": "没有可删除的任务", "count": 0}
    
    count = len(tasks)
    
    # 批量删除
    for task in tasks:
        db.delete(task)
    
    db.commit()
    
    return {"message": f"已清空 {count} 个任务", "count": count}
