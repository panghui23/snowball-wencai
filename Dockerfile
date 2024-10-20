# 使用官方的 Python 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /usr/src/app

# 安装 Node.js 16+
# 1. 安装 curl
# 2. 使用 NodeSource 安装 Node.js
RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*



# 复制 requirements.txt 并安装依赖
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt 

# 复制应用程序代码
COPY main.py ./

# 设置环境变量（可选）
# ENV PYTHONUNBUFFERED=1

# 指定容器启动时执行的命令
CMD ["python", "./main.py"]
