"""FastAPI 启动脚本"""
import uvicorn
import os
from dotenv import load_dotenv

# 加载环境变量 - 运行时环境变量优先于.env文件
load_dotenv(override=False)  # override=False 表示不覆盖已存在的环境变量

if __name__ == "__main__":
    # 从环境变量读取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"

    print(f"""
    ╔═══════════════════════════════════════╗
    ║   QwenImg Backend Server Starting    ║
    ╚═══════════════════════════════════════╝

    🚀 Server: http://{host}:{port}
    📚 API Docs: http://{host}:{port}/api/docs
    📖 ReDoc: http://{host}:{port}/api/redoc
    🔌 WebSocket: ws://{host}:{port}/ws/{{session_id}}

    Press CTRL+C to quit
    """)

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
