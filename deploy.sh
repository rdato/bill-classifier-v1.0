#!/bin/bash

# 账单分类工具 - 云服务器部署脚本
# 适用于 Ubuntu 20.04+

set -e

echo "======================================"
echo "  账单分类工具 - 云服务器部署"
echo "======================================"

# 配置变量
APP_DIR="/var/www/bill-classifier"
DOMAIN=""  # 留空使用 IP 访问

# 检查是否为 root
if [ "$EUID" -ne 0 ]; then
    echo "请使用 root 权限运行此脚本"
    exit 1
fi

# 1. 安装系统依赖
echo ""
echo "[1/6] 安装系统依赖..."
apt update
apt install -y python3 python3-pip python3-venv nginx nodejs npm

# 2. 创建应用目录
echo ""
echo "[2/6] 创建应用目录..."
mkdir -p $APP_DIR
mkdir -p $APP_DIR/uploads
mkdir -p $APP_DIR/outputs

# 3. 复制项目文件（假设当前目录为项目根目录）
echo ""
echo "[3/6] 复制项目文件..."
cp -r backend $APP_DIR/
cp -r frontend $APP_DIR/

# 4. 配置后端
echo ""
echo "[4/6] 配置后端..."
cd $APP_DIR/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# 5. 构建前端
echo ""
echo "[5/6] 构建前端..."
cd $APP_DIR/frontend
npm install
npm run build
mkdir -p $APP_DIR/dist
cp -r dist/* $APP_DIR/dist/

# 6. 配置 Nginx
echo ""
echo "[6/6] 配置 Nginx..."
cat > /etc/nginx/sites-available/bill-classifier << 'NGINX_CONF'
server {
    listen 80;
    server_name _;

    location / {
        root /var/www/bill-classifier/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        client_max_body_size 20M;
    }
}
NGINX_CONF

ln -sf /etc/nginx/sites-available/bill-classifier /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# 7. 配置后端服务
echo ""
echo "[7/7] 配置后端服务..."
cat > /etc/systemd/system/bill-classifier.service << 'SERVICE_CONF'
[Unit]
Description=Bill Classifier Web Application
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/bill-classifier/backend
ExecStart=/var/www/bill-classifier/backend/venv/bin/gunicorn -c gunicorn.conf.py wsgi:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE_CONF

systemctl daemon-reload
systemctl enable bill-classifier
systemctl start bill-classifier

# 完成
echo ""
echo "======================================"
echo "  部署完成！"
echo "======================================"
echo ""
echo "访问地址: http://你的服务器IP"
echo ""
echo "常用命令:"
echo "  查看状态: systemctl status bill-classifier"
echo "  重启服务: systemctl restart bill-classifier"
echo "  查看日志: journalctl -u bill-classifier -f"
echo ""
