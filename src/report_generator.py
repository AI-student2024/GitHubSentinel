# 文件路径: src/report_generator.py

import os  # 导入 os 模块用于处理文件路径和操作系统相关功能
from datetime import date, timedelta  # 导入 date 和 timedelta 模块用于日期计算
from logger import LOG  # 导入日志模块，用于记录日志信息

class ReportGenerator:
    def __init__(self, llm):
        """
        初始化 ReportGenerator 类，接收一个 LLM 实例用于生成报告。
        :param llm: LLM 类的实例，用于调用报告生成功能
        """
        self.llm = llm

    def export_daily_progress(self, repo, updates):
        """
        导出仓库的每日进展，生成 Markdown 文件。
        :param repo: 仓库的名称
        :param updates: 包含更新信息的字典
        :return: 生成的 Markdown 文件的路径
        """
        # 构建仓库的日志文件目录，将仓库名称中的斜杠替换为下划线
        repo_dir = os.path.join('daily_progress', repo.replace("/", "_"))
        os.makedirs(repo_dir, exist_ok=True)  # 如果目录不存在则创建
        
        # 创建并写入每日进展的 Markdown 文件
        file_path = os.path.join(repo_dir, f'{date.today()}.md')
        with open(file_path, 'w') as file:
            file.write(f"# Daily Progress for {repo} ({date.today()})\n\n")
            file.write("\n## Issues\n")
            for issue in updates['issues']:
                file.write(f"- {issue['title']} #{issue['number']}\n")
        
        return file_path  # 返回生成的文件路径

    def export_progress_by_date_range(self, repo, updates, days):
        """
        导出仓库在特定日期范围内的进展，生成 Markdown 文件。
        :param repo: 仓库的名称
        :param updates: 包含更新信息的字典
        :param days: 日期范围的天数
        :return: 生成的 Markdown 文件的路径
        """
        # 构建目录并写入特定日期范围的进展 Markdown 文件
        repo_dir = os.path.join('daily_progress', repo.replace("/", "_"))
        os.makedirs(repo_dir, exist_ok=True)

        today = date.today()
        since = today - timedelta(days=days)  # 计算起始日期
        
        date_str = f"{since}_to_{today}"  # 格式化日期范围字符串
        file_path = os.path.join(repo_dir, f'{date_str}.md')
        
        with open(file_path, 'w') as file:
            file.write(f"# Progress for {repo} ({since} to {today})\n\n")
            file.write(f"\n## Issues Closed in the Last {days} Days\n")
            for issue in updates['issues']:
                file.write(f"- {issue['title']} #{issue['number']}\n")
        
        LOG.info(f"Exported time-range progress to {file_path}")  # 记录导出日志
        return file_path  # 返回生成的文件路径

    def generate_daily_report(self, markdown_file_path):
        """
        读取 Markdown 文件并使用 LLM 生成每日报告。
        :param markdown_file_path: Markdown 文件的路径
        :return: 生成的报告内容及保存路径
        """
        with open(markdown_file_path, 'r') as file:
            markdown_content = file.read()  # 读取 Markdown 文件内容

        report = self.llm.generate_daily_report(markdown_content)  # 调用 LLM 生成报告

        report_file_path = os.path.splitext(markdown_file_path)[0] + "_report.md"
        with open(report_file_path, 'w+') as report_file:
            report_file.write(report)  # 将生成的报告内容写入文件

        LOG.info(f"Generated report saved to {report_file_path}")  # 记录生成报告日志
        
        return report, report_file_path  # 返回报告内容及保存路径

    def generate_report_by_date_range(self, markdown_file_path, days):
        """
        生成特定日期范围的报告，流程与日报生成类似。
        :param markdown_file_path: Markdown 文件的路径
        :param days: 日期范围的天数
        :return: 生成的报告内容及保存路径
        """
        with open(markdown_file_path, 'r') as file:
            markdown_content = file.read()  # 读取 Markdown 文件内容

        report = self.llm.generate_daily_report(markdown_content)  # 调用 LLM 生成报告

        report_file_path = os.path.splitext(markdown_file_path)[0] + f"_report.md"
        with open(report_file_path, 'w+') as report_file:
            report_file.write(report)  # 将生成的报告内容写入文件

        LOG.info(f"Generated report saved to {report_file_path}")  # 记录生成报告日志
        
        return report, report_file_path  # 返回报告内容及保存路径

    def generate_hackernews_report(self, news_content):
        # 确保目录存在
        base_dir = os.path.join("daily_progress", "hackernews")
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        # 生成原始信息的文件路径
        date_str = date.today().isoformat()
        news_file_path = os.path.join(base_dir, f"hackernews_{date_str}.md")

        # 保存抓取的新闻信息到文件
        with open(news_file_path, 'w+') as news_file:
            news_file.write(news_content)
        LOG.info(f"Hacker News 信息已保存到 {news_file_path}")

        # 调用 LLM 生成报告
        report = self.llm.generate_hackernews_report(news_content)

        # 生成报告文件路径，加上 _report 后缀
        report_file_path = os.path.join(base_dir, f"hackernews_{date_str}_report.md")

        # 保存报告到文件
        with open(report_file_path, 'w+') as report_file:
            report_file.write(report)
        LOG.info(f"Hacker News 技术趋势报告已保存到 {report_file_path}")

        return report, report_file_path  # 返回报告内容及保存路径