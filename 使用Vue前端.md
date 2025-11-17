# 使用 Vue 3 前端（推荐）

## 为什么换成 Vue？

React 前端在您的环境中有太多问题：
- ❌ 依赖冲突（@ant-design/icons）
- ❌ 启动失败
- ❌ 白屏问题

**Vue 3 + Element Plus 更稳定、更简单：**
- ✅ 依赖少，不容易出错
- ✅ 中文文档完善
- ✅ 社区成熟稳定
- ✅ 所有功能都支持（WebSocket、实时更新、并发任务）

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd frontend_vue
npm install
```

### 2. 启动后端（终端1）

```bash
# 回到项目根目录
cd ..

# 配置 API Key
export DASHSCOPE_API_KEY="sk-your-api-key-here"

# 启动后端
cd backend
python3 run.py
```

### 3. 启动前端（终端2）

```bash
# 进入 Vue 前端目录
cd frontend_vue

# 启动开发服务器
npm run dev
```

### 4. 访问应用

打开浏览器：**http://localhost:3000**

---

## ✨ 功能完整

新的 Vue 前端支持所有功能：

### 创作工具
- 📸 **文生图** - 根据文字描述生成图片
- 🎬 **图生视频** - 上传图片生成视频
- 🎥 **文生视频** - 根据文字生成视频场景

### 高级功能
- 🔄 **并发创作** - 同时创建多个任务
- 📊 **实时进度** - WebSocket 实时显示任务进度
- 📜 **历史记录** - 查看、筛选、删除历史任务
- 🎨 **美观界面** - Element Plus 精美组件

---

## 🎯 使用示例

### 文生图

1. 点击左侧菜单「文生图」
2. 输入提示词：`一只可爱的橘猫坐在窗台上，阳光洒在它身上`
3. 选择生成数量和尺寸
4. 点击「开始生成」
5. 右侧任务面板实时显示进度
6. 完成后自动显示结果

### 并发创作

- 创建任务后立即可以创建新任务
- 右侧面板显示所有活动任务
- 任务独立执行，互不影响

---

## 📦 项目结构

```
frontend_vue/
├── src/
│   ├── api/              # API 接口封装
│   ├── components/       # 所有组件
│   │   ├── TextToImage.vue
│   │   ├── ImageToVideo.vue
│   │   ├── TextToVideo.vue
│   │   ├── History.vue
│   │   └── ActiveTasks.vue
│   ├── stores/           # Pinia 状态管理
│   ├── types/            # TypeScript 类型定义
│   ├── App.vue           # 主应用组件
│   └── main.ts           # 入口文件
├── index.html
├── vite.config.ts        # Vite 配置（代理等）
├── package.json
└── README.md
```

---

## 🔧 技术栈

- **Vue 3.4** - 渐进式框架
- **Element Plus 2.5** - UI 组件库
- **Pinia 2.1** - 状态管理
- **Vite 5.0** - 构建工具
- **TypeScript 5.3** - 类型系统
- **Axios 1.6** - HTTP 客户端

---

## ⚠️ 常见问题

### 端口被占用

```bash
# 修改前端端口
# 编辑 frontend_vue/vite.config.ts
# 修改 server.port 的值
```

### 后端连接失败

检查：
1. 后端是否在 8000 端口运行
2. API Key 是否配置正确
3. 查看浏览器控制台错误信息

### npm install 失败

```bash
# 清理缓存重试
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

---

## 🎉 开始使用

现在试试新的 Vue 前端吧！应该不会再有依赖问题了！

如有问题，查看浏览器控制台（F12）获取详细错误信息。
