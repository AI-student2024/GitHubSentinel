# 文件路径: src/llm.py

import os  # 导入 os 模块用于处理操作系统相关功能
import json  # 导入 json 模块用于处理 JSON 数据
from openai import OpenAI  # 导入 OpenAI 库用于访问 GPT 模型
from logger import LOG  # 导入日志模块，用于记录日志信息

class LLM:
    def __init__(self, prompt_file="prompts/report_prompt.txt"):
        """
        初始化 LLM 类，加载系统提示信息并创建 OpenAI 客户端。
        :param prompt_file: 系统提示信息的文件路径，默认为 "prompts/report_prompt.txt"
        """
        self.client = OpenAI(
            api_key=os.getenv('WildtoOpenAI'),  # 使用环境变量中的 API 密钥
            base_url="https://api.gptsapi.net/v1"  # 使用自定义的 API 端点
        )
        self.system_prompt = self.load_prompt(prompt_file)  # 加载系统提示信息

    def load_prompt(self, prompt_file):
        """
        从指定的文件加载系统提示信息。
        :param prompt_file: 提示信息文件的路径
        :return: 加载的提示信息内容
        """
        if os.path.exists(prompt_file):
            with open(prompt_file, "r", encoding='utf-8') as file:
                return file.read()
        else:
            LOG.error(f"Prompt file {prompt_file} not found.")  # 记录错误日志
            return ""

    def generate_report(self, markdown_content, dry_run=False):
        """
        生成报告的通用方法。
        :param markdown_content: 输入的 Markdown 内容
        :param dry_run: 是否启用 dry run 模式（不实际调用 GPT 生成报告）
        :return: 生成的报告内容
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": markdown_content},
        ]

        if dry_run:
            # 如果启用了 dry run 模式，将提示信息保存到文件中
            self._save_prompt(messages, "daily_progress/prompt.txt")
            return "DRY RUN"

        LOG.info("使用 GPT 模型开始生成报告。")

        try:
            # 调用 OpenAI GPT 模型生成报告
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # 指定使用的模型版本
                messages=messages
            )
            LOG.debug("GPT response: {}", response)  # 记录 GPT 的响应信息
            return response.choices[0].message.content  # 返回生成的报告内容
        except Exception as e:
            LOG.error(f"生成报告时发生错误：{e}")  # 记录错误日志
            raise

    def generate_daily_report(self, markdown_content, dry_run=False):
        """
        为每日报告生成专用方法，调用通用报告生成方法。
        :param markdown_content: 输入的 Markdown 内容
        :param dry_run: 是否启用 dry run 模式
        :return: 生成的报告内容
        """
        return self.generate_report(markdown_content, dry_run)

    def generate_hackernews_report(self, news_content, dry_run=False):
        """
        为 Hacker News 报告生成专用方法。
        :param news_content: 输入的 Hacker News 内容
        :param dry_run: 是否启用 dry run 模式
        :return: 生成的报告内容
        """
        hackernews_prompt_file = "prompts/hackernews_prompt.txt"
        self.system_prompt = self.load_prompt(hackernews_prompt_file)  # 加载 Hacker News 专用的系统提示
        return self.generate_report(news_content, dry_run)

    def _save_prompt(self, messages, file_path):
        """
        将提示信息保存到指定文件。
        :param messages: 提示信息内容
        :param file_path: 文件保存路径
        """
        LOG.info("Dry run mode enabled. Saving prompt to file.")
        with open(file_path, "w+", encoding='utf-8') as f:
            json.dump(messages, f, indent=4, ensure_ascii=False)  # 格式化并保存提示信息
        LOG.debug(f"Prompt已保存到 {file_path}")
