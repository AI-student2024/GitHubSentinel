# 文件路径: src/config.py

import json  # 导入 json 模块用于处理 JSON 数据
import os  # 导入 os 模块用于处理操作系统相关功能

class Config:
    def __init__(self, config_file='config.json'):
        """
        初始化 Config 类，加载配置文件。
        :param config_file: 配置文件的路径，默认为 'config.json'
        """
        self.config_file = config_file
        self.load_config()  # 调用方法加载配置

    def load_config(self):
        """
        从配置文件中加载配置信息，优先从环境变量中获取敏感信息。
        """
        # 尝试从配置文件加载配置
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)  # 加载 JSON 数据为字典
        else:
            config = {}  # 如果配置文件不存在，使用空字典

        # GitHub 相关配置
        self.github_token = os.getenv('GITHUB_TOKEN', config.get('github_token', ''))

        # 电子邮件设置
        self.email = config.get('email', {})
        # 优先从环境变量中获取电子邮件密码
        self.email['password'] = os.getenv('EMAIL_PASSWORD', self.email.get('password', ''))

        # Hacker News 相关配置
        self.hackernews_frequency_days = config.get('hackernews_frequency_days', 1)
        self.hackernews_execution_time = config.get('hackernews_execution_time', "08:00")

        # GitHub 进展报告相关配置
        self.subscriptions_file = config.get('subscriptions_file', 'subscriptions.json')
        self.github_progress_frequency_days = config.get('github_progress_frequency_days', 1)
        self.github_progress_execution_time = config.get('github_progress_execution_time', "08:00")
