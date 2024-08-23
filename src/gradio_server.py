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

def reset_conditions():
    # 重新加载订阅列表并清空日期时间选择
    updated_subscriptions = subscription_manager.list_subscriptions()
    return updated_subscriptions, "", None, None

# 创建Gradio界面
with gr.Blocks() as demo:
    gr.Markdown("# GitHubSentinel", elem_id="title")
    
    with gr.Row():  # 时间控件在同一行
        start_date = gr.DateTime(label="开始日期时间", info="报告开始日期和时间")
        end_date = gr.DateTime(label="结束日期时间", info="报告结束日期和时间")
    
    repo_dropdown = gr.Dropdown(
        choices=subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目"
    )
    
    with gr.Row():  # 按钮在同一行
        submit_btn = gr.Button("生成报告")
        clear_btn = gr.Button("重置条件")

    markdown_output = gr.Markdown(elem_id="output", label="报告内容")
    file_output = gr.File(label="下载报告")
    
    submit_btn.click(
        export_progress_by_date_range,
        inputs=[repo_dropdown, start_date, end_date],
        outputs=[markdown_output, file_output]  # 恢复提交输出
    )
    
    # "重置条件"按钮的功能，只重置用户选择的输入，并重新加载订阅列表
    clear_btn.click(
        reset_conditions,
        inputs=[],
        outputs=[repo_dropdown, repo_dropdown, start_date, end_date],
    )
    
    # 给Markdown内容显示区域增加浅蓝色背景
    gr.HTML("""
    <style>
        #output {
            background-color: #e6f7ff;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
    """)

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))
