# Docker 部署

这个目录包含了 QwenImg 的 Docker 部署配置文件。

## 📦 文件说明

- `Dockerfile` - Docker 镜像构建文件
- `docker-compose.yml` - Docker Compose 配置
- `.dockerignore` - Docker 构建忽略文件

## 🚀 快速开始

### 使用 Docker Compose（推荐）

```bash
# 1. 配置环境变量
cp ../.env.example ../.env
nano ../.env  # 填入 DASHSCOPE_API_KEY

# 2. 启动服务
cd docker
docker-compose up -d

# 3. 访问应用
# 前端: http://localhost:5173
# 后端: http://localhost:8000
```

### 使用 Docker

```bash
# 1. 构建镜像
cd docker
docker build -t qwenimg -f Dockerfile ..

# 2. 运行容器
docker run -d \
  -p 8000:8000 \
  -p 5173:5173 \
  -e DASHSCOPE_API_KEY=your-key \
  --name qwenimg \
  qwenimg

# 3. 查看日志
docker logs -f qwenimg
```

## 🔧 配置说明

### 环境变量

在项目根目录的 `.env` 文件中配置：

```bash
DASHSCOPE_API_KEY=sk-your-api-key-here
DASHSCOPE_REGION=beijing
```

### 端口映射

- `8000` - 后端 API 端口
- `5173` - 前端界面端口

### 数据持久化

如需持久化数据，可以挂载卷：

```bash
docker run -d \
  -p 8000:8000 \
  -p 5173:5173 \
  -e DASHSCOPE_API_KEY=your-key \
  -v $(pwd)/data:/app/backend/outputs \
  -v $(pwd)/db:/app/backend \
  --name qwenimg \
  qwenimg
```

## 🛠️ 常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 重新构建
docker-compose up -d --build
```

## ⚠️ 注意事项

- 确保已安装 Docker 和 Docker Compose
- 首次启动可能需要较长时间下载依赖
- 生产环境建议使用反向代理（如 Nginx）
- 建议配置数据卷以持久化生成的图片和数据库

## 📚 更多信息

详细的部署指南请参考：[../DEPLOYMENT.md](../DEPLOYMENT.md)

---

**推荐使用本地安装以获得最佳开发体验！** 🎉
