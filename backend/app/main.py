"""FastAPI 主应用"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import logging

from .database import init_db
from .api import generation, websocket, inspiration

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="QwenImg API",
    description="阿里云通义万相多模态AI创作平台",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(generation.router)
app.include_router(inspiration.router)
app.include_router(websocket.router)

# 静态文件服务（用于保存生成的图片）
if not os.path.exists("./outputs"):
    os.makedirs("./outputs")
app.mount("/outputs", StaticFiles(directory="./outputs"), name="outputs")

# 前端静态文件（生产环境）
if os.path.exists("../frontend/dist"):
    app.mount("/assets", StaticFiles(directory="../frontend/dist/assets"), name="assets")


@app.on_event("startup")
async def startup_event():
    """启动时初始化数据库"""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized")

    # 添加示例灵感数据
    from .database import SessionLocal
    from .models import Inspiration

    db = SessionLocal()
    try:
        # 检查是否已有数据
        if db.query(Inspiration).count() == 0:
            logger.info("Adding sample inspirations...")
            sample_inspirations = [
                {
                    "category": "风景",
                    "title": "梦幻极光",
                    "prompt": "极光下的冰岛风景，星空璀璨，雪山倒影在湖面，8K超高清，电影级画质",
                    "negative_prompt": "低质量，模糊，噪点",
                    "task_type": "text_to_image",
                    "tags": ["风景", "极光", "自然"]
                },
                {
                    "category": "人物",
                    "title": "赛博朋克少女",
                    "prompt": "赛博朋克风格少女，霓虹灯光，未来城市背景，细节精致，高质量3D渲染",
                    "negative_prompt": "低质量，变形",
                    "task_type": "text_to_image",
                    "tags": ["人物", "赛博朋克", "科幻"]
                },
                {
                    "category": "动物",
                    "title": "梦幻水母",
                    "prompt": "发光的水母在深海游动，生物发光，神秘氛围，4K电影级",
                    "negative_prompt": "低质量",
                    "task_type": "text_to_video",
                    "tags": ["动物", "海洋", "梦幻"]
                },
                {
                    "category": "科幻",
                    "title": "星际飞船",
                    "prompt": "巨大的星际飞船穿越虫洞，科幻场景，光影效果震撼，8K画质",
                    "negative_prompt": "低质量，模糊",
                    "task_type": "text_to_video",
                    "tags": ["科幻", "太空", "飞船"]
                },
                {
                    "category": "艺术",
                    "title": "梵高星空",
                    "prompt": "梵高风格的星空，油画质感，色彩鲜艳，高清晰度",
                    "negative_prompt": "低质量，现代风格",
                    "task_type": "text_to_image",
                    "tags": ["艺术", "油画", "经典"]
                },
                {
                    "category": "建筑",
                    "title": "未来城市",
                    "prompt": "未来主义城市景观，摩天大楼，飞行汽车，日落时分，史诗级场景",
                    "negative_prompt": "低质量，现代建筑",
                    "task_type": "text_to_image",
                    "tags": ["建筑", "未来", "城市"]
                },
            ]

            for insp_data in sample_inspirations:
                inspiration = Inspiration(**insp_data)
                db.add(inspiration)

            db.commit()
            logger.info("Sample inspirations added")
    finally:
        db.close()


@app.get("/")
async def root():
    """根路径 - 返回前端页面"""
    if os.path.exists("../frontend/dist/index.html"):
        return FileResponse("../frontend/dist/index.html")
    return {
        "message": "QwenImg API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
