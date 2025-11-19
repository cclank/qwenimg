# Legacy Streamlit UI

这个目录包含了 QwenImg 的旧版 Streamlit Web 界面。

## 📝 说明

该版本已被新的 **FastAPI + React** 架构替代，提供了更现代化的用户体验和更强大的功能。

### 旧版特点
- 基于 Streamlit 框架
- Python 单文件应用 (`app.py`)
- 简单的 Web 界面
- 适合快速原型和演示

### 新版优势
- **FastAPI 后端** - 高性能异步 API
- **React 前端** - 现代化 UI/UX
- **WebSocket 实时通信** - 任务状态实时更新
- **更丰富的功能** - 拖拽上传、历史记录、任务管理等

## 🚀 如何使用旧版

如果你仍然想使用 Streamlit 版本：

### 1. 安装 Streamlit

```bash
pip install streamlit
```

### 2. 运行应用

```bash
# Linux/macOS
streamlit run legacy_streamlit_ui/app.py

# Windows
cd legacy_streamlit_ui
run_web_ui.bat
```

### 3. 访问应用

打开浏览器访问：http://localhost:8501

## ⚠️ 注意事项

- 旧版不再维护和更新
- 建议使用新版 FastAPI + React 架构
- 旧版可能缺少新功能和性能优化

## 🔄 迁移到新版

推荐使用新版本：

```bash
# 安装依赖
./install.sh

# 启动新版服务
./run.sh

# 访问新版界面
# http://localhost:5173
```

---

**推荐使用新版本以获得最佳体验！** 🎉
