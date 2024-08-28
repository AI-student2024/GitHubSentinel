# 文件路径: src/logger.py

from loguru import logger  # 导入 loguru 模块用于日志记录
import sys  # 导入 sys 模块用于访问系统相关功能
import os  # 导入 os 模块用于处理操作系统相关功能

# 定义统一的日志格式字符串
log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}"

# 日志文件目录
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)  # 如果日志目录不存在，则创建

# 移除 loguru 的默认日志配置
logger.remove()

# 配置日志输出到标准输出（控制台），日志级别为 DEBUG，支持彩色显示
logger.add(sys.stdout, level="DEBUG", format=log_format, colorize=True)

# 配置日志输出到标准错误，日志级别为 ERROR，支持彩色显示
logger.add(sys.stderr, level="ERROR", format=log_format, colorize=True)

# 配置日志输出到文件，日志文件大小达到 1 MB 时自动轮换，保留 10 个备份
log_file_path = os.path.join(log_dir, "app.log")
logger.add(log_file_path, rotation="1 MB", retention=10, level="DEBUG", format=log_format)

# 配置错误日志单独输出到 error.log 文件，文件大小达到 500 KB 时自动轮换，保留 5 个备份
error_log_file_path = os.path.join(log_dir, "error.log")
logger.add(error_log_file_path, level="ERROR", format=log_format, rotation="500 KB", retention=5)

# 为 logger 设置别名 LOG，方便在其他模块中导入和使用
LOG = logger

# 将 LOG 变量公开，允许其他模块通过 from logger import LOG 来使用它
__all__ = ["LOG"]
