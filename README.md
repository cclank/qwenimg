# QwenImg

**现代化的阿里云通义万相 AI 创作平台**

基于阿里云通义万相（Qwen）模型的 AI 创作平台，提供文生图、文生视频、图生视频等多模态生成能力。采用 FastAPI + React 架构，提供简洁优雅的 Web 界面。

## ✨ 特性

- 🚀 **极简 API** - 3 行代码即可生成图片或视频
- 🎨 **支持最新模型** - wan2.5-t2i-preview、wan2.5-i2v-preview、wan2.5-t2v-preview
- 🔧 **智能默认值** - 自动处理图片保存、尺寸调整等常见需求
- 📦 **返回标准对象** - 返回 PIL.Image 对象，方便后续处理
- 🌐 **灵活输入** - 支持本地文件、URL、Base64 等多种图片输入方式
- 🎯 **类型提示** - 完整的类型注解，IDE 友好
- 📖 **丰富示例** - 包含多个实用示例，快速上手

## 🎯 平台特色

QwenImg 是一个简洁、操作流畅、激发灵感的 AI 创作平台。我们专注于提供最直观的用户界面和最高效的创作体验，让您可以专注于创意本身，而不是复杂的操作流程。

![QwenImg 界面展示](https://raw.githubusercontent.com/cclank/qwenimg/main/docs/images/screenshot.png)

- 💡 **激发灵感** - 丰富的示例和模板帮助您快速启动创作
- ⚡ **操作流畅** - 响应式设计，提供丝滑般的用户体验
- 🎨 **简洁界面** - 专注于核心功能，去除一切不必要的干扰

## 📦 安装

### 环境要求

- Python 3.8 或更高版本（推荐使用 Python 3.12，Python 3.13 可能存在兼容性问题）
- pip（Python 包管理器）
- Node.js 16 或更高版本

### 🚀 一键安装（推荐）

我们提供了一个自动化脚本，可以一次性完成环境检查、依赖安装和配置。

**Linux / macOS:**

```bash
# 赋予执行权限
chmod +x install.sh

# 运行安装脚本
./install.sh
```

**安装脚本会自动执行以下操作：**
1. 检查系统环境（Python, Node.js）
2. 创建并配置 Python 虚拟环境
3. 安装后端依赖 (Python)
4. 安装前端依赖 (Node.js)
5. 自动配置 `.env` 环境变量文件
6. 恢复示例数据（如果有）

> ⚠️ **注意事项**：目前项目在 Python 3.13 版本上可能存在兼容性问题，建议使用 Python 3.12 或更低版本以确保顺利安装和运行。

## 🔑 API Key 配置

获取 API Key: [https://help.aliyun.com/zh/model-studio/get-api-key](https://help.aliyun.com/zh/model-studio/get-api-key)

**方式 1: 环境变量**

```bash
export DASHSCOPE_API_KEY="sk-xxx"
```

**方式 2: .env 文件**

创建 `.env` 文件：

```
DASHSCOPE_API_KEY=sk-xxx
```

**方式 3: 代码中传入**

```python
client = QwenImg(api_key="sk-xxx")
```

## 🚀 快速开始

### 🌐 方式一：Web 界面（推荐）

我们提供了基于 React 的现代化 Web 界面，体验更加流畅。

```bash
# 启动服务（同时启动前端和后端）
./start_dev.sh
```

启动后访问：
- 前端: http://localhost:3000
- 后端: http://localhost:8000

**功能特性：**
- ✨ 现代化 UI 设计
- ⚡️ 实时进度反馈
- 🖼️ 瀑布流作品展示
- 🎬 拖拽式图生视频
- 📱 移动端适配

*(注：旧版 Streamlit 界面已移动至 `legacy_streamlit_ui` 目录)*

### 🐍 方式二：Python 代码

#### 文生图 (Text-to-Image)

**最简单的用法 - 仅需 3 行代码：**

```python
from qwenimg import QwenImg

client = QwenImg()
image = client.text_to_image("一只可爱的猫")
```

就这么简单！图片会自动保存到 `./outputs` 目录，同时返回 PIL.Image 对象供你继续处理。

> 💡 **高级用法提示**：更多高级 Python 使用方式和调试技巧，请参阅 [高级 Python 使用指南](ADVANCED_PYTHON_USAGE.md)。

## 🌍 地域选择

```python
# 北京地域（默认）
client = QwenImg(region="beijing")

# 新加坡地域
client = QwenImg(region="singapore")
```

**注意：** 不同地域需要使用对应地域的 API Key。

## 📚 使用方式

### 🌐 Web 界面（推荐）

提供了基于 React 的现代化 Web 界面，无需编写代码即可使用所有功能：

```bash
# 启动服务
./start_dev.sh
```

启动后访问：
- 前端: http://localhost:3000
- 后端: http://localhost:8000

**停止服务：**
```bash
# 停止服务
./stop_dev.sh
```

**Web 界面功能：**
- ✅ 文生图 - 支持所有参数配置
- ✅ 图生视频 - 拖拽上传图片
- ✅ 文生视频 - 实时预览
- ✅ 图片下载 - 一键下载生成的图片
- ✅ 视频预览 - 在线播放生成的视频

### 📓 Jupyter Notebook

适合交互式学习和调试的完整教程：

```bash
cd examples
jupyter notebook complete_tutorial.ipynb
```

- `complete_tutorial.ipynb` - 覆盖所有使用场景，包含 10 个章节，40+ 代码示例

### 🐍 Python 脚本

位于 `examples/` 目录的示例脚本：

- `text_to_image_basic.py` - 基础文生图（3 行代码）
- `text_to_image_advanced.py` - 高级文生图用法
- `image_to_video.py` - 图生视频
- `text_to_video.py` - 文生视频
- `workflow.py` - 完整工作流示例
- `list_models.py` - 查看所有支持的模型

运行示例：

```bash
cd examples
python text_to_image_basic.py
python workflow.py
```

## 💡 设计理念

QwenImg 遵循以下设计原则：

1. **极简 API** - 3 行代码就能完成任务
2. **智能默认** - 自动处理常见需求（保存、格式转换等）
3. **灵活输入** - 支持多种输入方式
4. **标准输出** - 返回标准对象（PIL.Image）方便后续处理
5. **清晰边界** - 专注于图片和视频生成，不做无关功能

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [阿里云百炼](https://help.aliyun.com/zh/model-studio/)
- [DashScope API 文档](https://dashscope.aliyun.com/)
- [获取 API Key](https://help.aliyun.com/zh/model-studio/get-api-key)
- [通义万相文生图文档](https://help.aliyun.com/zh/model-studio/text-to-image-v2-api-reference)
- [通义万相图生视频文档](https://help.aliyun.com/zh/model-studio/image-to-video-api-reference)

## ⭐ Star History

如果这个项目对你有帮助，请给个 Star ⭐️

---

**Powered by Alibaba Cloud 百炼 & DashScope**
