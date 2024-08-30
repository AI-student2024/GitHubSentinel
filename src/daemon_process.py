# 文件路径: src/daemon_process.py

import schedule  # 导入 schedule 模块用于设置定时任务
import time  # 导入 time 模块用于控制时间间隔
import signal  # 导入 signal 模块用于处理系统信号
import sys  # 导入 sys 模块用于执行系统相关的操作

from config import Config  # 导入 Config 类用于加载配置信息
from github_client import GitHubClient  # 导入 GitHubClient 类用于与 GitHub API 交互
from notifier import Notifier  # 导入 Notifier 类用于发送通知
from report_generator import ReportGenerator  # 导入 ReportGenerator 类用于生成报告
from llm import LLM  # 导入 LLM 类用于生成报告内容
from subscription_manager import SubscriptionManager  # 导入 SubscriptionManager 类用于管理订阅
from hackernews_client import HackerNewsClient  # 导入 HackerNewsClient 类用于抓取 Hacker News 数据
from logger import LOG  # 导入日志记录器用于记录日志信息

def graceful_shutdown(signum, frame):
    """
    优雅关闭程序的函数，在接收到终止信号时调用。
    :param signum: 信号编号
    :param frame: 当前的堆栈帧
    """
    LOG.info("[优雅退出]守护进程接收到终止信号")
    sys.exit(0)  # 安全退出程序

def github_job(subscription_manager, github_client, report_generator, notifier, days):
    """
    定时执行 GitHub 仓库进展报告的任务。
    :param subscription_manager: SubscriptionManager 实例，用于管理订阅
    :param github_client: GitHubClient 实例，用于与 GitHub 交互
    :param report_generator: ReportGenerator 实例，用于生成报告
    :param notifier: Notifier 实例，用于发送通知
    :param days: 报告的日期范围
    """
    LOG.info("[开始执行GitHub定时任务]")
    subscriptions = subscription_manager.list_subscriptions()  # 获取当前所有订阅
    LOG.info(f"订阅列表：{subscriptions}")
    for repo in subscriptions:
        # 遍历每个订阅的仓库，导出进展并生成报告
        markdown_file_path = github_client.export_progress_by_date_range(repo, days)
        report, report_file_path = report_generator.generate_report_by_date_range(markdown_file_path, days)
        notifier.notify(repo, report)  # 发送通知
    LOG.info("[GitHub定时任务执行完毕]")

def hackernews_job(hackernews_client, report_generator, notifier):
    """
    定时执行 Hacker News 报告的任务。
    :param hackernews_client: HackerNewsClient 实例，用于抓取 Hacker News 数据
    :param report_generator: ReportGenerator 实例，用于生成 Hacker News 报告
    :param notifier: Notifier 实例，用于发送通知
    """
    LOG.info("[开始执行Hacker News定时任务]")
    news_content = hackernews_client.fetch_top_stories()  # 抓取最新的 Hacker News 头条新闻
    report, report_file_path = report_generator.generate_hackernews_report(news_content)
    notifier.notify("Hacker News", report)  # 发送 Hacker News 报告通知
    LOG.info("[Hacker News定时任务执行完毕]")

def main():
    """
    主函数，设置并启动定时任务。
    """
    # 设置信号处理器以处理优雅关闭
    signal.signal(signal.SIGTERM, graceful_shutdown)

    # 初始化配置和各类客户端
    config = Config()
    github_client = GitHubClient(config.github_token)
    hackernews_client = HackerNewsClient()
    notifier = Notifier(config.email)
    llm = LLM(config)
    report_generator = ReportGenerator(llm)
    subscription_manager = SubscriptionManager(config.subscriptions_file)

    # 启动时立即执行一次任务（如不需要可注释掉）
    github_job(subscription_manager, github_client, report_generator, notifier, config.github_progress_frequency_days)
    hackernews_job(hackernews_client, report_generator, notifier)

    # 安排每天的定时任务
    schedule.every(config.github_progress_frequency_days).days.at(
        config.github_progress_execution_time
    ).do(github_job, subscription_manager, github_client, report_generator, notifier, config.github_progress_frequency_days)

    schedule.every(config.hackernews_frequency_days).days.at(
        config.hackernews_execution_time
    ).do(hackernews_job, hackernews_client, report_generator, notifier)

    try:
        # 在守护进程中持续运行，等待定时任务触发
        while True:
            schedule.run_pending()  # 运行所有等待执行的任务
            time.sleep(1)  # 短暂休眠以减少 CPU 使用
    except Exception as e:
        LOG.error(f"主进程发生异常: {str(e)}")  # 记录异常信息
        sys.exit(1)  # 异常退出

if __name__ == '__main__':
    main()
