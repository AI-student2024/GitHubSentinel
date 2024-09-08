# 使用官方的 Python 基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目的所有文件到容器
COPY . .

# 确保validate_tests.sh的换行符和权限正确
RUN sed -i 's/\r$//' validate_tests.sh && chmod +x /app/validate_tests.sh && /app/validate_tests.sh

# 设置容器入口
CMD ["python", "src/daemon_process.py"]
