FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn gevent

# 复制代码
COPY . .

# 创建目录
RUN mkdir -p uploads outputs

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]
