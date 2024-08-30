# 文件路径: src/llm.py

import os  # 导入 os 模块用于处理操作系统相关功能
import json  # 导入 json 模块用于处理 JSON 数据
import requests # 导入 requests 库用于发送 HTTP 请求
from logger import LOG  # 导入日志模块，用于记录日志信息

class LLM:
    def __init__(self, config, prompt_file="prompts/report_prompt.txt"):
        """
        初始化 LLM 类，根据配置选择使用的模型（openai或ollama）。
        :param prompt_file: 系统提示信息的文件路径，默认为 "prompts/report_prompt.txt"
        :param config: 配置对象，包含所有的模型配置参数。
        """
        self.config = config
        self.model = config.llm_model_type.lower() # 获取配置文件中的模型类型，并转换为小写
        if self.model == 'openai':
            from openai import OpenAI  # 导入 OpenAI 库用于访问 GPT 模型

            # 创建 OpenAI 对象，并设置 API 密钥和自定义的 API 端点
            self.client = OpenAI(
                                 api_key=os.getenv('WildtoOpenAI'),  # 使用环境变量中的 API 密钥
                                 base_url="https://api.gptsapi.net/v1"  # 使用自定义的 API 端点
                                )

        elif self.model == 'ollama':
             self.api_url =config.ollama_api_url # 从配置中获取 Ollama API 端点
        else:
            raise ValueError(f"Unsupported model type: {self.model}")  # 如果模型类型不支持，则抛出错误

        self.system_prompt = self.load_prompt(prompt_file)  # 加载system prompt(系统角色的提示词)

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
        # 准备消息列表，包含系统提示和用户输入的内容
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": markdown_content},
        ]

        print("Messages sent to OpenAI API:", messages)  # 打印发送的消息内容

        if dry_run:
            # 如果启用了 dry run 模式，将提示信息保存到文件中
            self._save_prompt(messages, "daily_progress/prompt.txt")
            return "DRY RUN"
        
        # 根据选择的模型调用相应的生成报告方法
        if self.model == 'openai':
            return self._generate_report_openai(messages)
        elif self.model == 'ollama':
            return self._generate_report_ollama(messages)
        
    def _generate_report_openai(self, messages):
        """
        使用 OpenAI GPT 模型生成报告。
        :param messages: 提示信息内容
        :return: 生成的报告内容
        """
        LOG.info("使用 OpenAI GPT 模型开始生成报告。")
        try:
            # 调用 OpenAI GPT 模型生成报告
            response = self.client.chat.completions.create(
                model=self.config.openai_model_name,  # 使用配置中的OpenAI模型名称
                messages=messages
            )
            LOG.debug("GPT response: {}", response)  # 记录 GPT 的响应信息
            return response.choices[0].message.content  # 返回生成的报告内容
        except Exception as e:
            LOG.error(f"生成报告时发生错误：{e}")  # 记录错误日志
            raise
            

    def _generate_report_ollama(self, messages):
        """
        使用 Ollama 模型生成报告。
        :param messages: 提示信息内容
        :return: 生成的报告内容
        """
        LOG.info("使用 Ollama 模型开始生成报告。")
        try:
            payload ={
                "model": self.config.ollama_model_name, # 使用配置中的ollama模型名称
                "messages": messages,
                "stream": False

            }
            response = requests.post(self.api_url, json=payload) # 发送POST请求到Ollama API端点
            response_data = response.json() # 解析响应数据

            # 调试输出查看完整的响应结构
            LOG.debug("Ollama response: {}", response_data)

            # 直接从响应数据中获取content
            message_content = response_data.get("message",{}).get("content",None)
            if message_content:
                return message_content
            else:
                LOG.error("无法从响应中提取报告内容。")  # 记录错误日志
                raise ValueError("Invaalid response structure from Ollama API.")
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

if __name__ == "__main__":
    from config import Config
    config = Config()
    llm = LLM(config)

    markdown_content = """
# Progress for langchain-ai/langchain(2024-08-20 to 2024-08-21)

## Issues Closed in the Last 1 Days
- partners/chroma: release 0.1.3 #25599
- docs: few-shot conceptual guide #25596
- docs: update examples in api ref #25589
"""
    github_report = llm.generate_daily_report(markdown_content)
    print(github_report)

    news_content = """
# Hacker News Daily Report

## Top Stories
- [LangChain: A Framework for Building Applications with LLMs](https://news.ycombinator.com/item?id=35796806)
- [LangChain: A Framework for Building Applications with LLMs](https://news.ycombinator.com/item?id=35796806)
- [LangChain: A Framework for Building Applications with LLMs](https://news.ycombinator.com/item?id=35796806)
"""
    hackernews_report = llm.generate_hackernews_report(news_content)
    print(hackernews_report)


