# Dockerfile

# 使用官方的 Python 基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 并安装依赖
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目的所有文件
COPY . .

# 显式复制 validate_tests.sh
COPY validate_tests.sh /app/

# 确保文件有可执行权限
RUN chmod +x /app/validate_tests.sh

# 调试：列出 /app 目录中的文件，确保 validate_tests.sh 存在
RUN ls -la /app

# 执行测试脚本
RUN /app/validate_tests.sh


# 设置容器入口
CMD ["python", "src/daemon_process.py"]
