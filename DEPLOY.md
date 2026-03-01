# 云服务器部署指南

## 方式一：Docker 部署（推荐）

### 前提条件
- 云服务器（Ubuntu 20.04+ / CentOS 7+）
- 已安装 Docker 和 Docker Compose

### 部署步骤

```bash
# 1. 上传项目到服务器
scp -r bill-classifier-web root@your-server-ip:/opt/

# 2. 进入项目目录
cd /opt/bill-classifier-web

# 3. 一键启动
docker-compose up -d

# 4. 查看状态
docker-compose ps
```

访问：`http://你的服务器IP`

### 常用命令

```bash
# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新部署
git pull
docker-compose up -d --build
```

---

## 方式二：手动部署

### 1. 安装依赖

```bash
# Ubuntu
apt update
apt install -y python3 python3-pip python3-venv nginx nodejs npm

# CentOS
yum install -y python3 python3-pip nginx nodejs npm
```

### 2. 上传项目

```bash
# 方式1: scp 上传
scp -r bill-classifier-web root@your-server-ip:/var/www/

# 方式2: git clone
cd /var/www
git clone https://github.com/rdato/bill-classifier-v1.0 bill-classifier
```

### 3. 配置后端

```bash
cd /var/www/bill-classifier/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. 构建前端

```bash
cd /var/www/bill-classifier/frontend
npm install
npm run build
```

### 5. 配置 Nginx

```bash
# 复制配置
cp nginx.conf /etc/nginx/sites-available/bill-classifier
ln -s /etc/nginx/sites-available/bill-classifier /etc/nginx/sites-enabled/

# 修改配置中的路径和域名
nano /etc/nginx/sites-available/bill-classifier

# 测试并重启
nginx -t
systemctl restart nginx
```

### 6. 启动后端服务

```bash
# 复制服务配置
cp bill-classifier.service /etc/systemd/system/

# 启动服务
systemctl daemon-reload
systemctl enable bill-classifier
systemctl start bill-classifier
```

---

## 一键部署脚本

```bash
# 上传项目后，进入目录执行
chmod +x deploy.sh
./deploy.sh
```

---

## 安全建议

1. **配置防火墙**
```bash
ufw allow 80
ufw allow 443
ufw allow 22
ufw enable
```

2. **配置 HTTPS（可选）**
```bash
# 安装 certbot
apt install certbot python3-certbot-nginx

# 申请证书
certbot --nginx -d your-domain.com
```

3. **定期备份数据库**
```bash
# 备份 SQLite 数据库
cp /var/www/bill-classifier/backend/records.db /backup/records_$(date +%Y%m%d).db
```

---

## 服务器推荐配置

| 配置项 | 最低配置 | 推荐配置 |
|-------|---------|---------|
| CPU | 1核 | 2核 |
| 内存 | 1GB | 2GB |
| 硬盘 | 20GB | 40GB |
| 带宽 | 1Mbps | 3Mbps |

**推荐云服务商：**
- 阿里云轻量应用服务器（约 60元/年）
- 腾讯云轻量服务器（约 50元/年）
- 华为云 HECS（约 60元/年）
