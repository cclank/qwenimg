# QwenImg 部署指南

本文档介绍如何将 QwenImg 部署到生产环境。

## 📋 目录

- [Docker部署（推荐）](#docker部署推荐)
- [手动部署](#手动部署)
- [Nginx配置](#nginx配置)
- [SSL证书配置](#ssl证书配置)
- [性能优化](#性能优化)
- [监控和日志](#监控和日志)

## 🐳 Docker部署（推荐）

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+

### 快速部署

1. **克隆项目**
```bash
git clone https://github.com/cclank/qwenimg.git
cd qwenimg
```

2. **配置环境变量**
```bash
# 创建.env文件
echo "DASHSCOPE_API_KEY=your_api_key_here" > .env
```

3. **构建和启动**
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

4. **访问应用**

打开浏览器访问：http://your-server-ip:8000

### 停止服务

```bash
docker-compose down
```

### 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建
docker-compose build

# 重启服务
docker-compose restart
```

## 🔧 手动部署

### 系统要求

- Ubuntu 20.04+ / CentOS 8+
- Python 3.8+
- Node.js 16+
- Nginx（可选）

### 步骤

#### 1. 安装依赖

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm nginx
```

**CentOS/RHEL:**
```bash
sudo yum install python3 python3-pip nodejs npm nginx
```

#### 2. 克隆项目

```bash
cd /opt
sudo git clone https://github.com/cclank/qwenimg.git
cd qwenimg
sudo chown -R $USER:$USER .
```

#### 3. 设置后端

```bash
# 创建虚拟环境
cd backend
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env  # 编辑并填入API Key
```

#### 4. 构建前端

```bash
cd ../frontend
npm install
npm run build
```

构建产物将在 `frontend/dist` 目录。

#### 5. 配置Systemd服务

创建 `/etc/systemd/system/qwenimg.service`：

```ini
[Unit]
Description=QwenImg API Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/qwenimg/backend
Environment="PATH=/opt/qwenimg/backend/venv/bin"
ExecStart=/opt/qwenimg/backend/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable qwenimg
sudo systemctl start qwenimg
sudo systemctl status qwenimg
```

## 🌐 Nginx配置

### 基础配置

创建 `/etc/nginx/sites-available/qwenimg`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /opt/qwenimg/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket代理
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 输出文件
    location /outputs {
        alias /opt/qwenimg/outputs;
        autoindex off;
    }

    # 客户端最大上传大小
    client_max_body_size 100M;

    # 访问日志
    access_log /var/log/nginx/qwenimg_access.log;
    error_log /var/log/nginx/qwenimg_error.log;
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/qwenimg /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 性能优化配置

```nginx
# 启用gzip压缩
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript
           application/x-javascript application/xml+rss
           application/json application/javascript;

# 缓存静态资源
location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# 限流
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
location /api {
    limit_req zone=api_limit burst=20 nodelay;
    # ... 其他配置
}
```

## 🔒 SSL证书配置

### 使用 Let's Encrypt

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

Certbot会自动修改Nginx配置以启用HTTPS。

### 手动SSL配置

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ... 其他配置
}

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## ⚡ 性能优化

### 后端优化

1. **增加Worker数量**

编辑 `backend/run.py`：
```python
uvicorn.run(
    "app.main:app",
    host=host,
    port=port,
    workers=4,  # 根据CPU核心数调整
    reload=False
)
```

2. **使用Gunicorn**

```bash
pip install gunicorn uvicorn[standard]

gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile -
```

3. **使用PostgreSQL**

```bash
# 安装PostgreSQL
sudo apt install postgresql postgresql-contrib

# 创建数据库
sudo -u postgres createdb qwenimg

# 修改.env
DATABASE_URL=postgresql://user:password@localhost/qwenimg
```

### 前端优化

1. **启用CDN**

修改 `frontend/index.html`，使用CDN加载React等库。

2. **代码分割**

已在Vite中自动启用。

3. **压缩资源**

构建时自动启用。

## 📊 监控和日志

### 日志配置

**后端日志:**
```python
# backend/app/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/qwenimg/app.log'),
        logging.StreamHandler()
    ]
)
```

**Nginx日志:**
```bash
# 查看访问日志
tail -f /var/log/nginx/qwenimg_access.log

# 查看错误日志
tail -f /var/log/nginx/qwenimg_error.log
```

### 监控工具

**使用Prometheus + Grafana:**

1. 安装Prometheus exporter
```bash
pip install prometheus-fastapi-instrumentator
```

2. 添加到FastAPI
```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

3. 配置Prometheus抓取

### 健康检查

访问 http://your-domain.com/health 检查服务状态。

### 备份

**数据库备份:**
```bash
# SQLite
cp /opt/qwenimg/backend/qwenimg.db /backup/qwenimg_$(date +%Y%m%d).db

# PostgreSQL
pg_dump qwenimg > /backup/qwenimg_$(date +%Y%m%d).sql
```

**自动备份脚本:**
```bash
#!/bin/bash
# /opt/qwenimg/backup.sh

BACKUP_DIR="/backup/qwenimg"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
cp /opt/qwenimg/backend/qwenimg.db $BACKUP_DIR/db_$DATE.db

# 备份输出文件
tar -czf $BACKUP_DIR/outputs_$DATE.tar.gz /opt/qwenimg/outputs

# 删除30天前的备份
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

添加到crontab:
```bash
0 2 * * * /opt/qwenimg/backup.sh
```

## 🐛 故障排除

### 服务无法启动

```bash
# 检查服务状态
sudo systemctl status qwenimg

# 查看日志
sudo journalctl -u qwenimg -f

# 检查端口占用
sudo netstat -tulpn | grep 8000
```

### 数据库连接失败

```bash
# 检查数据库文件权限
ls -la /opt/qwenimg/backend/qwenimg.db

# 修复权限
sudo chown www-data:www-data /opt/qwenimg/backend/qwenimg.db
```

### Nginx 502错误

```bash
# 检查后端是否运行
curl http://127.0.0.1:8000/health

# 检查SELinux（CentOS）
sudo setsebool -P httpd_can_network_connect 1
```

## 📚 参考资源

- [FastAPI部署文档](https://fastapi.tiangolo.com/deployment/)
- [Nginx文档](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Docker文档](https://docs.docker.com/)

---

如有问题，请提交 [Issue](https://github.com/cclank/qwenimg/issues)。
