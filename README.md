# QwenImg

**现代化的阿里云通义万相 AI 创作平台**

基于阿里云通义万相（Qwen）模型的 AI 创作平台，提供文生图、文生视频、图生视频等多模态生成能力。采用 FastAPI + React 架构，提供简洁优雅的 Web 界面。

## ✨ 特性

- 🎨 **文生图** - 支持多种尺寸比例（1:1, 16:9, 9:16），一次生成 1-4 张
- 🎬 **文生视频** - 从文字描述直接生成视频（5-10秒，最高 1080P）
- 🖼️ **图生视频** - 将静态图片转换为动态视频
- 🚀 **现代化界面** - React 18 + TypeScript + Ant Design
- ⚡ **实时更新** - WebSocket 实时任务状态推送
- 📱 **响应式设计** - 完美适配桌面和移动端

## 📦 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- 阿里云 API Key

### 一键安装

```bash
# 1. 克隆项目
git clone <repository-url>
cd qwenimg

# 2. 运行安装脚本
./install.sh

# 3. 配置 API Key
nano .env  # 填入: DASHSCOPE_API_KEY=sk-your-key

# 4. 启动服务
./run.sh
```

### 访问应用

- **前端界面**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

> 💡 安装脚本会自动恢复 5 张示例图片，让新环境下的页面不会显得空荡荡。

## 🔑 获取 API Key

1. 访问 [阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/apiKey)
2. 登录/注册阿里云账号
3. 创建 API Key
4. 配置到 `.env` 文件

## 🎨 使用指南

### Web 界面

1. **创作对话框** - 页面底部浮动对话框，支持三种生成模式
2. **任务管理** - 右下角任务面板，实时显示进度
3. **历史记录** - 顶部导航查看所有生成记录
4. **拖拽创作** - 拖拽图片到对话框进行二次创作

### Python SDK

```python
from qwenimg import QwenImg

client = QwenImg()

# 文生图
image = client.text_to_image("一只可爱的猫")

# 图生视频
video_url = client.image_to_video(
    image="path/to/image.png",
    prompt="猫咪缓缓转头",
    duration=10
)

# 文生视频
video_url = client.text_to_video(
    prompt="一只柴犬在草地上奔跑",
    duration=10
)
```

## 🏗️ 项目结构

```
qwenimg/
├── backend/              # FastAPI 后端
│   ├── app/             # 应用核心
│   └── run.py           # 入口文件
├── frontend/            # React 前端
│   ├── src/             # 源代码
│   └── index.html       # 入口 HTML
├── qwenimg/             # Python SDK
├── demo_data_backup/    # 示例数据
├── docker/              # Docker 部署
├── examples/            # 示例代码
├── install.sh           # 一键安装
├── run.sh               # 启动服务
└── README.md            # 项目文档
```

## 🎯 支持的模型

- **文生图**: `wan2.5-t2i-preview`（默认）、`wanx-v1`
- **图生视频**: `wan2.5-i2v-preview`（默认）
- **文生视频**: `wan2.5-t2v-preview`（默认）

## 🔧 配置

在项目根目录的 `.env` 文件中配置：

```bash
# 必需
DASHSCOPE_API_KEY=sk-your-api-key-here

# 可选
DASHSCOPE_REGION=beijing  # 或 singapore
```

## 📝 常用命令

```bash
# 安装依赖
./install.sh

# 启动服务
./run.sh

# 停止服务
./stop_dev.sh

# 查看日志
tail -f logs/backend.log
tail -f logs/frontend.log
```

## 🚀 部署

### Docker 部署

```bash
cd docker
docker-compose up -d
```

详细说明：[docker/README.md](docker/README.md)

### 生产环境

参考 [DEPLOYMENT.md](DEPLOYMENT.md) 了解详细的生产环境部署指南。

## 🐛 故障排除

### 端口被占用

```bash
# 查找并杀死占用进程
lsof -i :8000  # 后端
lsof -i :5173  # 前端
kill -9 <PID>
```

### 依赖安装失败

```bash
# Python 依赖（使用国内镜像）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 前端依赖（使用淘宝镜像）
cd frontend
npm install --registry=https://registry.npmmirror.com
```

更多问题请参考：[TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关链接

- [阿里云百炼](https://help.aliyun.com/zh/model-studio/)
- [DashScope API 文档](https://dashscope.aliyun.com/)
- [获取 API Key](https://dashscope.console.aliyun.com/apiKey)

---

**Powered by Alibaba Cloud 百炼 & DashScope**
