# QwenImg 新前端架构文档

> 基于 FastAPI + React 的现代化多模态AI创作平台

## 🎨 项目概览

这是 QwenImg 项目的全新前后端分离架构，提供更流畅的用户体验和更强大的功能。

### ✨ 核心特性

- 🎯 **多模态创作**：支持文生图、文生视频、图生视频三种创作模式
- 🚀 **并发处理**：支持同时创建多个任务，互不影响
- 📡 **实时通信**：WebSocket实时推送任务进度和结果
- 💾 **历史记录**：SQLite数据库持久化存储所有创作历史
- 💡 **灵感画廊**：内置创作灵感库，激发用户创意
- 🎨 **现代UI**：基于Ant Design的精美界面设计
- 📱 **响应式**：完美适配桌面和移动设备

## 🏗️ 技术栈

### 后端
- **FastAPI** - 现代化Python Web框架
- **SQLAlchemy** - ORM数据库操作
- **WebSocket** - 实时双向通信
- **SQLite** - 轻量级数据库
- **ThreadPoolExecutor** - 异步任务处理

### 前端
- **React 18** - 用户界面库
- **TypeScript** - 类型安全
- **Vite** - 极速构建工具
- **Ant Design** - 企业级UI组件库
- **Zustand** - 轻量级状态管理
- **Axios** - HTTP客户端

## 📁 项目结构

```
qwenimg/
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── api/            # API路由
│   │   │   ├── generation.py   # 生成任务API
│   │   │   ├── websocket.py    # WebSocket路由
│   │   │   └── inspiration.py  # 灵感API
│   │   ├── models.py       # 数据库模型
│   │   ├── schemas.py      # Pydantic模型
│   │   ├── tasks.py        # 异步任务管理
│   │   ├── database.py     # 数据库配置
│   │   └── main.py         # FastAPI应用
│   ├── requirements.txt    # Python依赖
│   └── run.py             # 启动脚本
│
├── frontend/               # React前端
│   ├── src/
│   │   ├── components/    # React组件
│   │   │   ├── TextToImage.tsx      # 文生图
│   │   │   ├── ImageToVideo.tsx     # 图生视频
│   │   │   ├── TextToVideo.tsx      # 文生视频
│   │   │   ├── History.tsx          # 历史记录
│   │   │   ├── Inspiration.tsx      # 灵感画廊
│   │   │   ├── TaskCard.tsx         # 任务卡片
│   │   │   └── ActiveTasksPanel.tsx # 任务面板
│   │   ├── services/      # API服务
│   │   │   ├── api.ts             # REST API
│   │   │   └── websocket.ts       # WebSocket
│   │   ├── hooks/         # 自定义Hooks
│   │   ├── store/         # Zustand状态管理
│   │   ├── types/         # TypeScript类型
│   │   └── App.tsx        # 主应用
│   ├── package.json       # npm依赖
│   └── vite.config.ts     # Vite配置
│
└── qwenimg/               # 原核心库（后端依赖）
```

## 🚀 快速开始

### 前置要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn
- DashScope API Key（从[阿里云控制台](https://dashscope.console.aliyun.com/apiKey)获取）

### 1. 安装后端

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，填入你的API Key
```

### 2. 安装前端

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
# 或使用yarn
yarn install
```

### 3. 启动开发服务器

**启动后端（终端1）：**
```bash
cd backend
python run.py
```

后端将在 http://localhost:8000 启动

**启动前端（终端2）：**
```bash
cd frontend
npm run dev
```

前端将在 http://localhost:3000 启动

### 4. 访问应用

打开浏览器访问：**http://localhost:3000**

首次使用需要在设置中配置你的 DashScope API Key。

## 📖 API文档

启动后端后，访问以下地址查看自动生成的API文档：

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 🎯 使用指南

### 文生图

1. 点击左侧菜单「文生图」
2. 输入图片描述提示词
3. 选择模型、数量、尺寸等参数
4. 点击「开始生成」
5. 在右侧任务面板查看实时进度
6. 生成完成后自动显示结果

### 图生视频

1. 点击左侧菜单「图生视频」
2. 上传一张图片
3. 输入动作描述（可选）
4. 选择分辨率和时长
5. 点击「开始生成」
6. 等待视频生成完成

### 文生视频

1. 点击左侧菜单「文生视频」
2. 输入视频场景描述
3. 选择分辨率和时长
4. 点击「开始生成」
5. 等待视频生成完成

### 历史记录

1. 点击左侧菜单「历史记录」
2. 查看所有历史任务
3. 可以按类型、状态筛选
4. 支持删除不需要的记录

### 灵感画廊

1. 点击左侧菜单「灵感画廊」
2. 浏览各种创作灵感
3. 点击「复制」快速使用提示词
4. 点击「使用」直接创建任务

## 🔧 高级配置

### 修改后端端口

编辑 `backend/.env` 文件：
```env
PORT=8080  # 改为你想要的端口
```

### 修改前端代理

编辑 `frontend/vite.config.ts`：
```typescript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8080',  // 改为后端地址
      changeOrigin: true,
    },
  },
}
```

### 使用PostgreSQL

1. 安装PostgreSQL
2. 创建数据库
3. 修改 `backend/.env`：
```env
DATABASE_URL=postgresql://user:password@localhost/qwenimg
```
4. 安装依赖：
```bash
pip install psycopg2-binary
```

## 📦 生产部署

### 构建前端

```bash
cd frontend
npm run build
```

构建产物在 `frontend/dist` 目录。

### 启动生产服务器

```bash
cd backend
# 设置环境变量
export RELOAD=false

# 使用uvicorn启动
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

后端会自动服务前端静态文件，访问 http://localhost:8000 即可。

### Docker部署（推荐）

创建 `Dockerfile`：

```dockerfile
# 后端
FROM python:3.10-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
COPY qwenimg/ ../qwenimg/

# 前端构建
FROM node:18 as frontend
WORKDIR /app
COPY frontend/package*.json .
RUN npm install
COPY frontend/ .
RUN npm run build

# 最终镜像
FROM python:3.10-slim
WORKDIR /app
COPY --from=0 /app .
COPY --from=frontend /app/dist ./frontend/dist
CMD ["python", "run.py"]
```

### Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 🐛 故障排除

### 后端启动失败

1. 检查Python版本：`python --version`
2. 检查依赖安装：`pip list`
3. 检查API Key配置：`cat .env`
4. 查看日志输出

### 前端无法连接后端

1. 检查后端是否启动
2. 检查Vite代理配置
3. 检查浏览器控制台错误
4. 检查CORS配置

### WebSocket连接失败

1. 检查后端WebSocket路由
2. 检查防火墙设置
3. 检查Nginx配置（如果使用）
4. 查看浏览器Network面板

### 任务生成失败

1. 检查API Key是否有效
2. 检查网络连接
3. 查看后端日志
4. 检查DashScope服务状态

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 联系方式

- GitHub: https://github.com/cclank/qwenimg
- Issues: https://github.com/cclank/qwenimg/issues

---

**享受创作吧！** 🎨✨
