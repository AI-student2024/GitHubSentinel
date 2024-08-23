# src/gradio_server.py

import gradio as gr  # 导入gradio库用于创建GUI
from datetime import datetime  # 用于日期处理

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)

def export_progress_by_date_range(repo, since, until):
    # 将since和until参数转换为字符串格式
    since_str = datetime.fromtimestamp(since).strftime("%Y-%m-%dT%H:%M:%S")
    until_str = datetime.fromtimestamp(until).strftime("%Y-%m-%dT%H:%M:%S")
    
    # 执行报告生成逻辑
    raw_file_path = github_client.export_progress_by_date_range(repo, since_str, until_str)
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, since_str, until_str)

    return report, report_file_path

# 创建Gradio界面
demo = gr.Interface(
    fn=export_progress_by_date_range,
    title="GitHubSentinel",
    inputs=[
        gr.Dropdown(
            subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目"
        ),
        gr.DateTime(label="开始日期时间", info="报告开始日期和时间"),
        gr.DateTime(label="结束日期时间", info="报告结束日期和时间"),
    ],
    outputs=[gr.Markdown(), gr.File(label="下载报告")]
)

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))
