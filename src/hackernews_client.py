# 文件路径：src/hackernews_client.py
import os
import requests  # 导入 requests 库用于发送 HTTP 请求
from datetime import datetime, date, timedelta  # 导入日期处理模块
from bs4 import BeautifulSoup  # 导入 BeautifulSoup 库用于解析 HTML
from urllib.parse import urljoin  # 导入 urljoin 用于处理相对 URL
from logger import LOG  # 导入日志模块

class HackerNewsClient:
    def __init__(self, config):
        """
        初始化 HackerNewsClient 类。
        :param config: 传入conig.Config 类的实例
        """
        self.config = config   # 使用配置实例
        self.base_url = config.hackernews_base_url # 使用配置中的 Hacker News 网站的基本 URL
        self.max_items = config.hackernews_max_items # 使用配置中的 Hacker News 网站的最大新闻数量

    def fetch_top_stories(self):
        """
        抓取 Hacker News 网站的头条新闻。
        :param max_items: 要抓取的新闻数量
        :return: 返回markdown文件的路径
        """
        max_items = self.max_items

        try:
            # 发送 HTTP GET 请求获取 Hacker News 首页内容
            response = requests.get(self.base_url)
            response.raise_for_status()  # 检查请求是否成功
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Hacker News: {e}")
            return ""

        # 解析 HTML 内容
        soup = BeautifulSoup(response.text, 'html.parser')
        stories = soup.find_all('tr', class_='athing')  # 查找所有包含新闻的 <tr> 标签

        formatted_stories = []
        for story in stories[:self.max_items]:  # 限制返回的新闻数量
            title_tag = story.find('span', class_='titleline').find('a')
            if title_tag:
                title = title_tag.text  # 获取新闻标题
                link = title_tag['href']  # 获取新闻链接
                full_link = urljoin(self.base_url, link)  # 确保链接是完整的 URL
                formatted_stories.append(f"### {title}\nLink: {full_link}\n")
        
        LOG.debug(f"[准备导出hackernews每日新闻]:")
        today = datetime.now().date().isoformat()  # 获取今天的日期
        hackernews_dir = os.path.join('daily_progress', "hackernews")  # 构建存储路径
        os.makedirs(hackernews_dir, exist_ok=True)  # 确保目录存在
        
        file_path = os.path.join(hackernews_dir, f'hackernews_{today}.md')  # 构建文件路径
        with open(file_path, 'w') as file:
            file.write(f"# Daily Progress for hackernews ({today})\n\n")
            for story in formatted_stories:  # 写入今天的新闻
                file.write(f"{story}\n")
        
        LOG.info(f"[hackernews每日新闻文件生成： {file_path}]")  # 记录日志
        return file_path
        
        
if __name__ == "__main__":
    # 测试 HackerNewsClient 类的功能
    from config import Config  # 导入配置管理类
    config = Config()
    client = HackerNewsClient(config)

    formatted_stories = client.fetch_top_stories()
    if formatted_stories:
        print(formatted_stories)
    else:
        print("No stories found.")