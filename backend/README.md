# Backend 后端目录

## 📁 目录说明

这是 QwenImg 项目的 FastAPI 后端代码目录。

### 文件结构

```
backend/
├── app/                    # 应用代码
│   ├── api/               # API路由
│   ├── models.py          # 数据库模型
│   ├── schemas.py         # Pydantic模型
│   ├── tasks.py           # 异步任务管理
│   ├── database.py        # 数据库配置
│   └── main.py            # FastAPI应用
├── run.py                 # 启动脚本
└── README.md              # 本文件
```

## ⚙️ 配置文件位置

**重要：所有配置文件都在项目根目录，不在backend目录！**

```
项目根目录/
├── requirements.txt       # Python依赖（包含FastAPI等）
├── .env.example          # 环境变量示例
├── .env                  # 实际配置（需自行创建）
└── backend/              # 后端代码目录
```

## 🚀 启动方式

**从项目根目录启动，不要在backend目录下启动！**

```bash
# 1. 返回项目根目录
cd ..

# 2. 安装依赖（从根目录）
pip3 install -r requirements.txt

# 3. 配置环境变量
export DASHSCOPE_API_KEY="your_api_key"

# 4. 启动服务（推荐使用启动脚本）
./start_dev.sh

# 或手动启动
cd backend && python3 run.py
```

## 📝 注意事项

1. **依赖安装**：使用根目录的 `requirements.txt`
2. **环境配置**：使用根目录的 `.env` 文件
3. **启动脚本**：使用根目录的 `start_dev.sh`
4. **数据库**：SQLite数据库文件会在backend目录下生成（qwenimg.db）

## 🔗 相关文档

- [快速开始](../QUICKSTART.md)
- [完整文档](../README_NEW_FRONTEND.md)
- [故障排除](../TROUBLESHOOTING.md)
