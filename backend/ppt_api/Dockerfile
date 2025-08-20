FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录的内容到工作目录
COPY . /app

# 复制生产环境配置文件
RUN cp /app/.env_prod /app/.env
# 创建日志目录
RUN mkdir /app/logs

# 升级pip
RUN python -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip setuptools wheel

# 安装Agent依赖
RUN pip install --no-cache-dir -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple  -r requirements.txt


# 设置时区为东八区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 设置环境变量，知道是在容器中运行
ENV DOCKER_ENV=1
# 禁用 Python 的输出缓冲，print出来的内容实时输出到docker logs中
ENV PYTHONUNBUFFERED=1

CMD ["python", "main_api.py"]