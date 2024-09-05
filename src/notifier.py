# 文件路径: src/notifier.py

import smtplib  # 导入 smtplib 模块用于发送邮件
import markdown2  # 导入 markdown2 模块用于将 Markdown 转换为 HTML
from email.mime.text import MIMEText  # 导入 MIMEText 用于构建邮件正文
from email.mime.multipart import MIMEMultipart  # 导入 MIMEMultipart 用于构建包含附件的邮件
from logger import LOG  # 导入日志模块，用于记录日志信息

class Notifier:
    def __init__(self, email_settings):
        """
        初始化 Notifier 类，设置电子邮件配置。
        :param email_settings: 包含电子邮件服务器信息的字典
        """
        self.email_settings = email_settings
    
    def notify(self, subject, report, report_type="gitHub"):
        """
        发送通知邮件。
        :param subject: 邮件主题
        :param report: 报告内容
        :param report_type: 报告类型（默认值为 "GitHub"）
        """
        if self.email_settings:
            self.send_email(subject, report, report_type)
        else:
            LOG.warning("邮件设置未配置正确，无法发送通知")
    
    def send_email(self, subject, report, report_type):
        """
        发送电子邮件，包含生成的报告。
        :param subject: 邮件主题
        :param report: 报告内容
        :param report_type: 报告类型，用于在邮件中区分不同类型的报告
        """
        LOG.info(f"准备发送 {report_type} 报告的邮件")
        msg = MIMEMultipart()
        msg['From'] = self.email_settings['from']
        msg['To'] = self.email_settings['to']
        msg['Subject'] = f"[GitHubSentinel] {subject} {report_type} 报告"
        
        # 将Markdown内容转换为HTML
        html_report = markdown2.markdown(report)

        msg.attach(MIMEText(html_report, 'html'))  # 将HTML格式的报告内容附加到邮件中

        try:
            # 连接到SMTP服务器并发送邮件
            with smtplib.SMTP_SSL(self.email_settings['smtp_server'], self.email_settings['smtp_port']) as server:
                LOG.debug("登录SMTP服务器")
                server.login(self.email_settings['from'], self.email_settings['password'])
                server.sendmail(msg['From'], msg['To'], msg.as_string())
                LOG.info(f"{report_type} 报告邮件发送成功！")
        except smtplib.SMTPException as e:
            LOG.error(f"发送邮件失败：{str(e)}")

if __name__ == '__main__':
    from config import Config  # 导入 Config 类用于加载配置
    config = Config()
    notifier = Notifier(config.email)

    # GitHub 项目测试
    test_repo = "DjangoPeng/openai-quickstart"
    test_github_report = """
# DjangoPeng/openai-quickstart 项目进展

## 时间周期：2024-08-24

## 新增功能
- Assistants API 代码与文档

## 主要改进
- 适配 LangChain 新版本

## 修复问题
- 关闭了一些未解决的问题。

"""
    notifier.notify(test_repo, test_github_report, report_type="GitHub")

    # Hacker News 报告测试
    test_hackernews_report = """
# Hacker News 技术趋势报告

## 头条新闻
1. [OpenAI 发布新 API](https://news.ycombinator.com/item?id=12345)
2. [LangChain 推出 2.0 版本](https://news.ycombinator.com/item?id=67890)

## 技术趋势分析
- 大模型 API 正在成为新的开发范式
- 自然语言处理工具链正在快速扩展
"""
    notifier.notify("Hacker News", test_hackernews_report, report_type="Hacker News")