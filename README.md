# QwenImg

**现代化的阿里云通义万相 AI 创作平台**

基于阿里云通义万相（Qwen）模型的 AI 创作平台，提供文生图、文生视频、图生视频等多模态生成能力。采用 FastAPI + React 架构，提供简洁优雅的 Web 界面。

![QwenImg 界面展示](docs/images/screenshot.png)

## ✨ 特性

- 🚀 **极简 API** - 3 行代码即可生成图片或视频
- 🎨 **支持最新模型** - wan2.5-t2i-preview、wan2.5-i2v-preview、wan2.5-t2v-preview
- 🔧 **智能默认值** - 自动处理图片保存、尺寸调整等常见需求
- 📦 **返回标准对象** - 返回 PIL.Image 对象，方便后续处理
- 🌐 **灵活输入** - 支持本地文件、URL、Base64 等多种图片输入方式
- 🎯 **类型提示** - 完整的类型注解，IDE 友好
- 📖 **丰富示例** - 包含多个实用示例，快速上手

## 📦 安装

### 环境要求

- Python 3.8 或更高版本
- pip（Python 包管理器）

### 完整安装步骤

**1. 克隆或下载项目**

```bash
git clone <repository-url>
cd qwenimg
```

**2. 创建虚拟环境（推荐）**

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

**3. 安装依赖**

方式一：安装为可编辑包（推荐开发使用）

```bash
pip install -e .
```

方式二：仅安装依赖

```bash
pip install -r requirements.txt
```

方式三：手动安装

```bash
pip install dashscope pillow requests python-dotenv
```

**4. 验证安装**

```bash
python -c "from qwenimg import QwenImg; print('QwenImg installed successfully!')"
```

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

### 🌐 方式一：Web 界面（推荐，零代码）

最简单的使用方式，无需编写任何代码！

```bash
# Linux/macOS
./run_web_ui.sh

# Windows
run_web_ui.bat

# 或者手动启动
streamlit run app.py
```

然后访问 `http://localhost:8501`，在浏览器中使用所有功能！

### 🐍 方式二：Python 代码

#### 文生图 (Text-to-Image)

**最简单的用法 - 仅需 3 行代码：**

```python
from qwenimg import QwenImg

client = QwenImg()
image = client.text_to_image("一只可爱的猫")
```

就这么简单！图片会自动保存到 `./outputs` 目录，同时返回 PIL.Image 对象供你继续处理。

**高级用法：**

```python
# 生成高质量图片，自定义参数
image = client.text_to_image(
    prompt="一位身穿白色长袍的古风男子，眉心有朱砂痣，仙侠风格，4K高清",
    negative_prompt="模糊、粗糙、色彩暗淡",
    model="wan2.5-t2i-preview",
    size="1024*1024",  # 或 "720*1280"（竖版）、"1280*720"（横版）
    n=4,  # 一次生成 4 张
    seed=12345,  # 固定随机种子以重现结果
    output_dir="./my_images"
)

# 生成多张图片
images = client.text_to_image("美丽的风景", n=4)
for i, img in enumerate(images, 1):
    print(f"Image {i}: {img.size}")
```

#### 图生视频 (Image-to-Video)

```python
# 从图片生成视频
video_url = client.image_to_video(
    image="path/to/image.png",  # 支持本地文件、URL、Base64
    prompt="角色缓缓转身，云雾翻涌",
    duration=10,  # 5 或 10 秒
    resolution="1080P"  # "480P"、"720P"、"1080P"
)

print(f"视频生成成功: {video_url}")
```

**高级用法：**

```python
# 详细的时间轴控制
video_url = client.image_to_video(
    image="image.png",
    prompt="""([锚定设定]，严格依据图片生成10秒视频)
    ([动态分层]，前景云雾流动，角色长发随风摆动)
    ([时间轴分层]，0-3秒：展现场景；4-7秒：聚焦角色；8-10秒：镜头上移)
    ([技术参数]，60帧每秒，4K画质)""",
    negative_prompt="模糊、抖动、失真",
    resolution="1080P",
    duration=10,
    seed=12345
)

# 使用 Base64（适合私密图片）
video_url = client.image_to_video(
    image="image.png",
    prompt="描述动作",
    use_base64=True  # 将图片编码为 Base64
)

# 添加音频
video_url = client.image_to_video(
    image="image.png",
    prompt="描述动作",
    audio="path/to/audio.mp3"  # 支持本地文件或 URL
)
```

#### 文生视频 (Text-to-Video)

```python
# 直接从文字生成视频
video_url = client.text_to_video(
    prompt="一只柴犬在草地上奔跑，阳光明媚，春天",
    duration=10,
    resolution="1080P"
)

print(f"视频生成成功: {video_url}")
```

#### 完整工作流：文生图 -> 图生视频

```python
from qwenimg import QwenImg

client = QwenImg()

# 1. 生成图片
image = client.text_to_image(
    prompt="一位古风男子站在云雾缭绕的山间",
    output_dir="./workflow"
)

# 2. 用生成的图片制作视频
video_url = client.image_to_video(
    image="./workflow/xxx.png",  # 使用上一步生成的图片
    prompt="云雾流动，长发飘逸",
    duration=10
)

print(f"工作流完成！视频: {video_url}")
```

## 🎯 支持的模型

### 文生图模型

- `wan2.5-t2i-preview` - 万相 2.5 文生图预览版（默认，最新）
- `wanx-v1` - 通义万相 V1

### 图生视频模型

- `wan2.5-i2v-preview` - 万相 2.5 图生视频预览版（默认，最新）

### 文生视频模型

- `wan2.5-t2v-preview` - 万相 2.5 文生视频预览版（默认，最新）

**查看所有模型：**

```python
from qwenimg import QwenImg

# 查看所有模型
models = QwenImg.list_models()

# 查看特定类型
t2i_models = QwenImg.list_models("t2i")
i2v_models = QwenImg.list_models("i2v")
t2v_models = QwenImg.list_models("t2v")
```

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

提供了基于 Streamlit 的可视化 Web 界面，无需编写代码即可使用所有功能：

```bash
# 安装 Streamlit
pip install streamlit

# 运行 Web 界面
streamlit run app.py
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

## 🎨 API 参考

### QwenImg 类

#### `__init__(api_key=None, endpoint=None, region="beijing")`

初始化客户端。

**参数：**
- `api_key` (str, optional): API Key，默认从环境变量读取
- `endpoint` (str, optional): API 端点 URL
- `region` (str, optional): 地域，"beijing" 或 "singapore"

#### `text_to_image(prompt, **kwargs)`

文生图。

**参数：**
- `prompt` (str): 图片描述
- `model` (str): 模型名称，默认 "wan2.5-t2i-preview"
- `negative_prompt` (str): 负面提示词
- `n` (int): 生成数量，1-4
- `size` (str): 尺寸，如 "1024*1024"
- `seed` (int): 随机种子
- `prompt_extend` (bool): 是否自动扩展提示词
- `watermark` (bool): 是否添加水印
- `save` (bool): 是否保存到磁盘
- `output_dir` (str): 保存目录
- `return_pil` (bool): 是否返回 PIL.Image 对象

**返回：**
- 单张图片时：PIL.Image 对象或文件路径
- 多张图片时：PIL.Image 对象列表或文件路径列表

#### `image_to_video(image, **kwargs)`

图生视频。

**参数：**
- `image` (str): 图片路径、URL 或 Base64
- `model` (str): 模型名称，默认 "wan2.5-i2v-preview"
- `prompt` (str): 视频描述
- `negative_prompt` (str): 负面提示词
- `audio` (str): 音频路径或 URL
- `resolution` (str): 分辨率，"480P"/"720P"/"1080P"
- `duration` (int): 时长，5 或 10 秒
- `seed` (int): 随机种子
- `watermark` (bool): 是否添加水印
- `use_base64` (bool): 是否使用 Base64 编码图片

**返回：**
- str: 视频 URL

#### `text_to_video(prompt, **kwargs)`

文生视频。

**参数：**
- `prompt` (str): 视频描述
- `model` (str): 模型名称，默认 "wan2.5-t2v-preview"
- `negative_prompt` (str): 负面提示词
- `resolution` (str): 分辨率，"480P"/"720P"/"1080P"
- `duration` (int): 时长，5 或 10 秒
- `seed` (int): 随机种子
- `watermark` (bool): 是否添加水印

**返回：**
- str: 视频 URL

#### `list_models(model_type="all")` (静态方法)

列出支持的模型。

**参数：**
- `model_type` (str): "t2i"、"i2v"、"t2v" 或 "all"

**返回：**
- dict: 模型信息字典

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
