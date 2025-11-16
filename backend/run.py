"""FastAPI 启动脚本"""
import uvicorn
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

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
