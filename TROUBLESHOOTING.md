# 故障排除指南

## 🔧 常见问题及解决方案

### 1. ModuleNotFoundError: No module named 'uvicorn'

**问题**：后端启动失败，提示找不到uvicorn模块

**原因**：Python依赖未安装

**解决方案**：

```bash
# 方式1: 使用安装脚本（推荐）
./install.sh

# 方式2: 手动安装
cd backend
pip3 install -r requirements.txt

# 方式3: 使用虚拟环境（最佳实践）
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**验证安装**：
```bash
python3 -c "import uvicorn; print('✅ uvicorn已安装')"
```

---

### 2. 前端白屏问题

**问题**：浏览器访问http://localhost:3000显示白屏

**可能原因**：
- 后端未启动或启动失败
- 前端依赖未安装
- API Key未配置

**解决步骤**：

**Step 1: 检查后端是否运行**
```bash
# 检查后端进程
ps aux | grep "python.*run.py"

# 检查后端端口
curl http://localhost:8000/health

# 如果失败，查看后端日志
tail -f logs/backend.log
```

**Step 2: 检查前端依赖**
```bash
cd frontend

# 重新安装依赖
rm -rf node_modules package-lock.json
npm install

# 启动前端
npm run dev
```

**Step 3: 检查浏览器控制台**
- 按F12打开开发者工具
- 查看Console标签页的错误信息
- 查看Network标签页的网络请求

---

### 3. API Key相关错误

**问题**：启动时提示API Key未配置，或任务创建失败

**解决方案**：

**方式1: 环境变量（推荐）**
```bash
export DASHSCOPE_API_KEY="sk-your-api-key-here"
./start_dev.sh
```

**方式2: .env文件**
```bash
# 创建配置文件
cp backend/.env.example backend/.env

# 编辑文件
nano backend/.env

# 修改这一行：
DASHSCOPE_API_KEY=sk-your-api-key-here
```

**验证配置**：
```bash
# 检查环境变量
echo $DASHSCOPE_API_KEY

# 或检查.env文件
cat backend/.env | grep DASHSCOPE_API_KEY
```

**获取API Key**：
https://dashscope.console.aliyun.com/apiKey

---

### 4. 端口占用

**问题**：启动失败，提示端口已被占用

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

**方案1: 停止占用端口的进程**
```bash
# 找到进程PID
lsof -i :8000

# 停止进程
kill <PID>
```

**方案2: 修改端口**
```bash
# 后端端口
export PORT=8080

# 前端端口 - 编辑 frontend/vite.config.ts
# 修改 server.port 值
```

---

### 5. WebSocket连接失败

**问题**：实时进度更新不工作

**检查**：
```bash
# 查看浏览器控制台
# 应该看到：WebSocket已连接: <session_id>

# 如果看到错误：
# - 检查后端是否运行
# - 检查防火墙设置
```

**解决方案**：
```bash
# 重启服务
./stop_dev.sh
./start_dev.sh

# 清除浏览器缓存
# Chrome: Ctrl+Shift+Delete
# Firefox: Ctrl+Shift+Delete
```

---

### 6. 依赖安装失败

**问题**：pip install或npm install失败

**Python依赖安装失败**：
```bash
# 升级pip
pip3 install --upgrade pip

# 使用国内镜像
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 使用虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**npm依赖安装失败**：
```bash
# 清除缓存
npm cache clean --force

# 删除旧依赖
cd frontend
rm -rf node_modules package-lock.json

# 重新安装
npm install

# 使用国内镜像
npm install --registry=https://registry.npmmirror.com

# 或使用yarn
npm install -g yarn
yarn install
```

---

### 7. 虚拟环境问题

**问题**：使用虚拟环境时依赖找不到

**解决方案**：
```bash
# 创建虚拟环境
cd backend
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 运行服务（保持虚拟环境激活状态）
python run.py
```

**start_dev.sh会自动检测并激活虚拟环境！**

---

### 8. 数据库错误

**问题**：SQLite相关错误

**解决方案**：
```bash
# 删除旧数据库
cd backend
rm qwenimg.db

# 重启后端（会自动创建新数据库）
cd ..
./stop_dev.sh
./start_dev.sh
```

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
```

**查看完整日志**：
```bash
# 后端
cat logs/backend.log

# 前端
cat logs/frontend.log
```

---

### 10. 完全重置

**当一切都不工作时**：

```bash
# 1. 停止所有服务
./stop_dev.sh

# 2. 清理所有依赖
rm -rf backend/venv
rm -rf frontend/node_modules
rm -rf frontend/package-lock.json
rm -rf logs/*
rm -rf backend/qwenimg.db

# 3. 重新安装
./install.sh

# 4. 配置API Key
export DASHSCOPE_API_KEY="sk-your-api-key-here"

# 5. 启动
./start_dev.sh
```

---

## 🆘 获取帮助

如果以上方案都无法解决问题：

1. **查看日志文件**
   ```bash
   cat logs/backend.log
   cat logs/frontend.log
   ```

2. **检查系统环境**
   ```bash
   python3 --version
   node --version
   npm --version
   ```

3. **提交Issue**
   - 访问：https://github.com/cclank/qwenimg/issues
   - 包含：错误信息、日志文件、系统环境

4. **查看完整文档**
   - [快速开始指南](QUICKSTART.md)
   - [完整文档](README_NEW_FRONTEND.md)
   - [部署文档](DEPLOYMENT.md)

---

## ✅ 验证安装

**验证Python环境**：
```bash
python3 --version  # 应该 >= 3.8
pip3 --version
python3 -c "import uvicorn, fastapi; print('✅ 依赖OK')"
```

**验证Node.js环境**：
```bash
node --version    # 应该 >= 16
npm --version
```

**验证服务运行**：
```bash
# 后端健康检查
curl http://localhost:8000/health

# 前端访问
curl http://localhost:3000
```

---

## 💡 最佳实践

1. **总是使用虚拟环境**（Python）
2. **定期更新依赖**
3. **使用环境变量存储敏感信息**
4. **查看日志文件排查问题**
5. **遇到问题先搜索Issues**

---

**祝你使用愉快！** 🎉
