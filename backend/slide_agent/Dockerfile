# 使用轻量 Python 镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 拷贝依赖文件并安装
COPY requirements.txt ./
RUN pip install -i  https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --no-cache-dir -r requirements.txt

# 拷贝其余代码文件
COPY . .

ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 10011
EXPOSE 10012

# 启动命令
CMD ["python", "main_api.py"]
