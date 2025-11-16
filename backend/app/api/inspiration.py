"""灵感示例API - 激发用户创作"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..schemas import InspirationCreate, InspirationResponse, InspirationListResponse
from ..models import Inspiration

router = APIRouter(prefix="/api/inspiration", tags=["inspiration"])


@router.get("/list", response_model=InspirationListResponse)
async def get_inspirations(
    category: Optional[str] = None,
    task_type: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """获取灵感列表"""
    query = db.query(Inspiration)

    if category:
        query = query.filter(Inspiration.category == category)
    if task_type:
        query = query.filter(Inspiration.task_type == task_type)

    total = query.count()
    inspirations = query.order_by(Inspiration.likes.desc()).limit(limit).all()

    # 获取所有分类
    categories = db.query(Inspiration.category).distinct().all()
    categories = [c[0] for c in categories]

    return InspirationListResponse(
        inspirations=[
            InspirationResponse(
                id=insp.id,
                category=insp.category,
                title=insp.title,
                prompt=insp.prompt,
                negative_prompt=insp.negative_prompt,
                thumbnail_url=insp.thumbnail_url,
                task_type=insp.task_type,
                tags=insp.tags,
                likes=insp.likes,
                created_at=insp.created_at
            )
            for insp in inspirations
        ],
        total=total,
        categories=categories
    )


@router.get("/{inspiration_id}", response_model=InspirationResponse)
async def get_inspiration(inspiration_id: int, db: Session = Depends(get_db)):
    """获取单个灵感详情"""
    inspiration = db.query(Inspiration).filter(Inspiration.id == inspiration_id).first()
    if not inspiration:
        raise HTTPException(status_code=404, detail="灵感不存在")

    return InspirationResponse(
        id=inspiration.id,
        category=inspiration.category,
        title=inspiration.title,
        prompt=inspiration.prompt,
        negative_prompt=inspiration.negative_prompt,
        thumbnail_url=inspiration.thumbnail_url,
        task_type=inspiration.task_type,
        tags=inspiration.tags,
        likes=inspiration.likes,
        created_at=inspiration.created_at
    )


@router.post("/create", response_model=InspirationResponse)
async def create_inspiration(inspiration: InspirationCreate, db: Session = Depends(get_db)):
    """创建灵感示例（管理员功能）"""
    db_inspiration = Inspiration(
        category=inspiration.category,
        title=inspiration.title,
        prompt=inspiration.prompt,
        negative_prompt=inspiration.negative_prompt,
        thumbnail_url=inspiration.thumbnail_url,
        task_type=inspiration.task_type,
        tags=inspiration.tags
    )
    db.add(db_inspiration)
    db.commit()
    db.refresh(db_inspiration)

    return InspirationResponse(
        id=db_inspiration.id,
        category=db_inspiration.category,
        title=db_inspiration.title,
        prompt=db_inspiration.prompt,
        negative_prompt=db_inspiration.negative_prompt,
        thumbnail_url=db_inspiration.thumbnail_url,
        task_type=db_inspiration.task_type,
        tags=db_inspiration.tags,
        likes=db_inspiration.likes,
        created_at=db_inspiration.created_at
    )


@router.post("/{inspiration_id}/like")
async def like_inspiration(inspiration_id: int, db: Session = Depends(get_db)):
    """点赞灵感"""
    inspiration = db.query(Inspiration).filter(Inspiration.id == inspiration_id).first()
    if not inspiration:
        raise HTTPException(status_code=404, detail="灵感不存在")

    inspiration.likes += 1
    db.commit()

    return {"message": "点赞成功", "likes": inspiration.likes}


@router.get("/categories/list")
async def get_categories(db: Session = Depends(get_db)):
    """获取所有分类"""
    categories = db.query(Inspiration.category).distinct().all()
    return {"categories": [c[0] for c in categories]}
