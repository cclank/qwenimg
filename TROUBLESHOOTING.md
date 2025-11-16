# 故障排除指南

## 🔧 常见问题及解决方案

### 1. ModuleNotFoundError: No module named 'uvicorn'

**问题**：后端启动失败，提示找不到uvicorn模块

**原因**：Python依赖未安装，或安装环境与运行环境不一致

**解决方案**：

#### 方式1：使用安装脚本（推荐）
```bash
./install.sh
```

#### 方式2：手动安装（在项目根目录）
```bash
pip3 install -r requirements.txt
```

#### 方式3：使用虚拟环境（最佳实践）
```bash
# 在项目根目录创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

**环境一致性检查**：
```bash
# 启动服务后，查看日志中显示的Python路径
tail logs/backend.log

# 应该看到类似：
# 📍 当前Python: /path/to/your/python3

# 确认依赖安装在同一位置
pip3 show uvicorn
# Location字段应该和Python路径匹配
```

**验证安装**：
```bash
python3 -c "import uvicorn; print('✅ uvicorn已安装，版本:', uvicorn.__version__)"
python3 -c "import fastapi; print('✅ fastapi已安装')"
python3 -c "import sqlalchemy; print('✅ sqlalchemy已安装')"
python3 -c "import dashscope; print('✅ dashscope已安装')"
```

**常见原因分析**：

| 原因 | 症状 | 解决方法 |
|-----|------|---------|
| 安装时未用虚拟环境，运行时激活了venv | `pip list` 能看到包，但导入失败 | 删除venv或在venv内重新安装 |
| 系统有多个Python版本 | 安装到了Python 3.9，运行用了3.11 | 使用 `python3 -m pip` 而不是 `pip3` |
| 权限问题 | 安装失败或安装到用户目录 | 使用虚拟环境或 `pip3 install --user` |

---

### 2. 前端白屏问题

**问题**：浏览器访问http://localhost:3000显示白屏

**可能原因**：
- 后端未启动或启动失败
- 前端依赖未安装
- API Key未配置
- JavaScript错误

**解决步骤**：

#### Step 1: 检查后端是否运行
```bash
# 检查后端进程
ps aux | grep "python.*run.py"

# 检查后端端口
curl http://localhost:8000/health
# 应该返回：{"status":"healthy"}

# 如果失败，查看后端日志
tail -f logs/backend.log
```

#### Step 2: 检查前端依赖
```bash
cd frontend

# 重新安装依赖
rm -rf node_modules package-lock.json
npm install

# 启动前端开发服务器
npm run dev
```

#### Step 3: 检查浏览器控制台
- 按 `F12` 打开开发者工具
- 查看 **Console** 标签页的错误信息
- 查看 **Network** 标签页，确认API请求正常
- 常见错误：
  - `Failed to fetch` - 后端未启动
  - `CORS error` - 后端CORS配置问题（已修复）
  - `Unexpected token` - JavaScript语法错误

#### Step 4: 清除缓存
```bash
# 浏览器硬刷新
# Chrome/Edge: Ctrl+Shift+R
# Firefox: Ctrl+F5
# Safari: Cmd+Option+R

# 或清除浏览器缓存
# Chrome: Ctrl+Shift+Delete
```

---

### 3. API Key相关错误

**问题**：启动时提示API Key未配置，或任务创建失败

**正确的配置方式**：

#### 方式1：环境变量（推荐）
```bash
export DASHSCOPE_API_KEY="sk-your-api-key-here"
./start_dev.sh
```

**优势**：
- 不会提交到Git
- 优先级最高
- 易于在不同环境切换

#### 方式2：.env文件
```bash
# 复制示例配置（在项目根目录）
cp .env.example .env

# 编辑文件
nano .env  # 或使用其他编辑器

# 修改这一行：
DASHSCOPE_API_KEY=sk-your-api-key-here
```

**配置优先级**：
```
运行时环境变量 > .env 文件
```

**验证配置**：
```bash
# 检查环境变量
echo $DASHSCOPE_API_KEY

# 或检查.env文件（在项目根目录）
cat .env | grep DASHSCOPE_API_KEY

# 测试API Key是否有效
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"task_type":"text_to_image","params":{"prompt":"测试"}}'
```

**获取API Key**：
https://dashscope.console.aliyun.com/apiKey

---

### 4. 端口占用

**问题**：启动失败，提示端口已被占用

```
Error: Address already in use (port 8000)
```

**检查端口占用**：
```bash
# 检查8000端口（后端）
lsof -i :8000
# 或
netstat -tuln | grep 8000

# 检查3000端口（前端）
lsof -i :3000
```

**解决方案**：

#### 方案1：停止占用端口的进程
```bash
# 使用项目提供的停止脚本
./stop_dev.sh

# 或手动停止
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill
lsof -i :3000 | grep LISTEN | awk '{print $2}' | xargs kill
```

#### 方案2：修改端口
```bash
# 后端端口 - 编辑根目录 .env 文件
PORT=8080

# 前端端口 - 编辑 frontend/vite.config.ts
# 修改 server.port 值
```

---

### 5. WebSocket连接失败

**问题**：实时进度更新不工作，创建任务后看不到进度

**症状**：
- 浏览器控制台显示 WebSocket connection failed
- 任务状态一直是 pending
- 进度条不更新

**检查**：
```bash
# 1. 查看浏览器控制台（F12）
# 应该看到：WebSocket已连接: <session_id>

# 2. 检查后端日志
tail -f logs/backend.log
# 应该看到 WebSocket 连接日志

# 3. 测试 WebSocket 端点
# 访问：ws://localhost:8000/ws/<your-session-id>
```

**解决方案**：

```bash
# 1. 重启服务
./stop_dev.sh
./start_dev.sh

# 2. 检查防火墙设置
# 确保允许 8000 端口的 WebSocket 连接

# 3. 清除浏览器缓存
# Chrome: Ctrl+Shift+Delete
# Firefox: Ctrl+Shift+Delete

# 4. 检查代理设置
# WebSocket 可能被代理阻止
```

---

### 6. 依赖安装失败

**问题**：`pip install` 或 `npm install` 失败

#### Python依赖安装失败

**常见错误**：
- `error: Microsoft Visual C++ 14.0 is required` (Windows)
- `Unable to find vcvarsall.bat` (Windows)
- `gcc: command not found` (Linux)
- `Connection timeout`

**解决方案**：

```bash
# 1. 升级pip
pip3 install --upgrade pip

# 2. 使用国内镜像（网络慢时）
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 使用虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. 安装编译工具（Linux）
sudo apt-get install python3-dev build-essential

# 5. 安装编译工具（macOS）
xcode-select --install

# 6. 一个一个安装（排查具体是哪个包有问题）
pip3 install uvicorn
pip3 install fastapi
pip3 install sqlalchemy
pip3 install dashscope
```

#### npm依赖安装失败

```bash
cd frontend

# 1. 清除缓存
npm cache clean --force

# 2. 删除旧依赖
rm -rf node_modules package-lock.json

# 3. 重新安装
npm install

# 4. 使用国内镜像
npm install --registry=https://registry.npmmirror.com

# 5. 使用yarn作为替代
npm install -g yarn
yarn install

# 6. 使用pnpm（更快）
npm install -g pnpm
pnpm install
```

---

### 7. 虚拟环境问题

**问题**：虚拟环境和系统Python混淆

**症状**：
- 明明安装了依赖，但还是找不到
- `which pip` 和 `which python` 指向不同的环境
- 依赖重复安装

**完整的虚拟环境使用流程**：

```bash
# 1. 在项目根目录创建虚拟环境
python3 -m venv venv

# 2. 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 3. 验证激活成功
which python3  # 应该显示 venv/bin/python3
which pip3     # 应该显示 venv/bin/pip3

# 4. 安装依赖
pip install -r requirements.txt

# 5. 运行服务
./start_dev.sh  # 脚本会自动检测并使用venv

# 6. 退出虚拟环境（完成工作后）
deactivate
```

**start_dev.sh 会自动检测并激活虚拟环境！**
- 支持 `venv/` 和 `.venv/` 两种命名
- 自动显示当前使用的 Python 路径
- 自动检查依赖并安装

---

### 8. 数据库错误

**问题**：SQLite相关错误

```
sqlite3.OperationalError: database is locked
sqlite3.DatabaseError: file is not a database
```

**解决方案**：

```bash
# 1. 停止所有服务
./stop_dev.sh

# 2. 删除旧数据库（在项目根目录）
rm qwenimg.db

# 3. 重启后端（会自动创建新数据库）
./start_dev.sh

# 4. 如果使用 PostgreSQL
# 检查 .env 中的 DATABASE_URL
DATABASE_URL=postgresql://user:password@localhost:5432/qwenimg
```

**数据库文件位置**：
- SQLite: `./qwenimg.db`（项目根目录）
- 可以通过 `.env` 中的 `DATABASE_URL` 修改

---

### 9. 日志查看

**实时查看日志**：
```bash
# 后端日志
tail -f logs/backend.log

# 前端日志
tail -f logs/frontend.log

# 同时查看两个日志
tail -f logs/*.log

# 只看错误
tail -f logs/backend.log | grep -i error
```

**查看完整日志**：
```bash
# 后端
cat logs/backend.log

# 前端
cat logs/frontend.log

# 查看最后50行
tail -50 logs/backend.log
```

**日志位置**：
- 后端日志：`logs/backend.log`
- 前端日志：`logs/frontend.log`
- 进程PID：`logs/backend.pid`, `logs/frontend.pid`

---

### 10. 完全重置

**当一切都不工作时，执行完全重置**：

```bash
# 1. 停止所有服务
./stop_dev.sh

# 2. 清理所有依赖和缓存（在项目根目录）
rm -rf venv .venv
rm -rf frontend/node_modules
rm -rf frontend/package-lock.json
rm -rf logs/*
rm -rf qwenimg.db
rm -rf __pycache__ backend/__pycache__ backend/app/__pycache__

# 3. 重新安装依赖
# 使用虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd frontend
npm install
cd ..

# 4. 配置API Key
export DASHSCOPE_API_KEY="sk-your-api-key-here"

# 5. 启动服务
./start_dev.sh
```

---

## 🆘 获取帮助

如果以上方案都无法解决问题：

### 1. 收集诊断信息

```bash
# 系统环境
python3 --version
node --version
npm --version
pip3 --version

# 当前Python路径
which python3
which pip3

# 已安装的关键依赖
pip3 list | grep -E "uvicorn|fastapi|sqlalchemy|dashscope"

# 端口占用情况
lsof -i :8000
lsof -i :3000

# 日志文件
cat logs/backend.log
cat logs/frontend.log
```

### 2. 常见错误模式

| 错误信息 | 可能原因 | 解决方案编号 |
|---------|---------|------------|
| `ModuleNotFoundError: No module named 'uvicorn'` | 依赖未安装 | #1 |
| 前端白屏 | 后端未启动/前端依赖问题 | #2 |
| `Address already in use` | 端口被占用 | #4 |
| WebSocket连接失败 | 服务未启动/防火墙阻止 | #5 |
| `database is locked` | 数据库文件被锁定 | #8 |
| API Key错误 | 配置未生效 | #3 |

### 3. 提交Issue

访问：https://github.com/cclank/qwenimg/issues

包含以下信息：
- 操作系统和版本
- Python版本和Node.js版本
- 完整的错误日志
- 已尝试的解决方案
- 系统诊断信息（见上方）

### 4. 查看文档

- [快速开始指南](QUICKSTART.md)
- [项目README](README_NEW_FRONTEND.md)
- [环境配置](.env.example)

---

## ✅ 自检清单

**启动前确认**：

- [ ] Python 3.8+ 已安装
- [ ] Node.js 16+ 已安装
- [ ] 依赖已安装（`pip3 list | grep uvicorn`）
- [ ] API Key已配置（环境变量或.env文件）
- [ ] 端口 8000 和 3000 未被占用
- [ ] 当前在项目根目录
- [ ] 执行权限已设置（`chmod +x *.sh`）
- [ ] 配置文件在根目录（requirements.txt, .env）

**启动后确认**：

- [ ] 后端进程存在（`ps aux | grep run.py`）
- [ ] 前端进程存在（`ps aux | grep vite`）
- [ ] 后端健康检查通过（`curl http://localhost:8000/health`）
- [ ] 前端页面可访问（http://localhost:3000）
- [ ] WebSocket 已连接（浏览器控制台）
- [ ] 可以创建任务并看到实时进度

---

## 💡 最佳实践

1. **总是使用虚拟环境**（Python）
   - 避免依赖冲突
   - 便于项目隔离

2. **使用环境变量存储敏感信息**
   - 不要提交 .env 到 Git
   - 使用 .env.example 作为模板

3. **定期查看日志文件**
   - 及时发现问题
   - 了解系统运行状态

4. **遇到问题先看日志**
   - `tail -f logs/backend.log`
   - 浏览器控制台（F12）

5. **保持依赖更新**
   - 定期运行 `pip install --upgrade`
   - 定期运行 `npm update`

6. **配置文件统一在根目录**
   - `requirements.txt` - Python依赖
   - `.env` - 环境变量配置
   - 启动脚本都在根目录运行

---

**祝你使用愉快！** 🎉
