# 文件路径: src\gradio_server.py

import gradio as gr  # 导入 gradio 库用于创建 GUI
from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于 GitHub API 操作的客户端
from hackernews_client import HackerNewsClient  # 导入用于 Hacker News 操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的 LLM 类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from notifier import Notifier  # 导入通知模块
from logger import LOG  # 导入日志记录器

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
hackernews_client = HackerNewsClient(config)  # 新增 Hacker News 客户端实例
llm = LLM(config)
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)
notifier = Notifier(config.email)  # 创建 Notifier 实例用于发送邮件
report_types = config.report_types

def export_progress_by_date_range(repo, days, send_email=False):
    try:
        # 导出和生成指定时间范围内 GitHub 项目的进展报告
        report_type = report_types[0]
        raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
        report, report_file_path = report_generator.generate_daily_report(raw_file_path,report_type)  # 生成并获取报告内容及文件路径
        LOG.info(f"报告生成成功: {report_file_path}")

        email_status = "未发送"
        if send_email:
            notifier.notify(subject=repo, report=report, report_type=report_type)  # 发送报告邮件
            email_status = "发送成功"
            LOG.info(f"GitHub 报告邮件发送成功")
        return report, report_file_path, email_status  # 返回报告内容、报告文件路径及邮件发送状态

    except Exception as e:
        LOG.error(f"生成报告或发送邮件时出错: {str(e)}")
        return f"错误: {str(e)}", None, "发送失败"

def generate_hackernews_report(send_email=False):
    try:
        # 抓取 Hacker News 头条新闻并生成报告
        report_type = report_types[1]
        raw_file_path = hackernews_client.fetch_top_stories()  # 获取 Hacker News 头条新闻
        report, report_file_path = report_generator.generate_daily_report(raw_file_path, report_type)  # 生成 Hacker News 报告
        LOG.info(f"Hacker News 报告生成成功: {report_file_path}")

        email_status = "未发送"
        if send_email:
            notifier.notify(subject="Hacker News", report=report, report_type=report_type)  # 发送报告邮件
            email_status = "发送成功"
            LOG.info(f"Hacker News 报告邮件发送成功")
        return report, report_file_path, email_status  # 返回报告内容、报告文件路径及邮件发送状态

    except Exception as e:
        LOG.error(f"生成报告或发送邮件时出错: {str(e)}")
        return f"错误: {str(e)}", None, "发送失败"

# 创建 Gradio 界面
with gr.Blocks() as demo:
    gr.Markdown("# GitHub Sentinel")  # 主标题

    # GitHub 进展报告部分
    with gr.Tab("GitHub Report"):
        gr.Markdown("### 生成 GitHub 项目进展报告")
        repo_dropdown = gr.Dropdown(
            subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅 GitHub 项目"
        )  # 下拉菜单选择订阅的 GitHub 项目
        days_slider = gr.Slider(
            value=2, minimum=1, maximum=7, step=1, label="报告周期", info="生成项目过去一段时间进展，单位：天"
        )  # 滑动条选择报告的时间范围
        send_email_checkbox = gr.Checkbox(label="发送报告邮件", info="生成报告后自动发送邮件")

        github_report_output = gr.Markdown()
        github_file_output = gr.File(label="下载报告")
        email_status_output = gr.Textbox(label="邮件发送状态", interactive=False)

        # 按钮触发 GitHub 报告生成
        gr.Button("生成报告").click(
            export_progress_by_date_range, 
            inputs=[repo_dropdown, days_slider, send_email_checkbox],
            outputs=[github_report_output, github_file_output, email_status_output]
        )

    # Hacker News 报告部分
    with gr.Tab("Hacker News Report"):
        gr.Markdown("### 生成 Hacker News 技术趋势报告")
        send_email_checkbox_hn = gr.Checkbox(label="发送报告邮件", info="生成报告后自动发送邮件")

        hackernews_report_output = gr.Markdown()
        hackernews_file_output = gr.File(label="下载报告")
        email_status_output_hn = gr.Textbox(label="邮件发送状态", interactive=False)

        # 按钮触发 Hacker News 报告生成
        gr.Button("生成 Hacker News 报告").click(
            generate_hackernews_report,
            inputs=[send_email_checkbox_hn],
            outputs=[hackernews_report_output, hackernews_file_output, email_status_output_hn]
        )

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")  # 启动界面并设置为公共可访问