# Gunicorn 配置文件
import multiprocessing

# 绑定地址
bind = "0.0.0.0:5000"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 线程数
threads = 2

# 超时时间
timeout = 120

# 守护进程
daemon = False

# 日志
accesslog = "-"
errorlog = "-"
loglevel = "info"
