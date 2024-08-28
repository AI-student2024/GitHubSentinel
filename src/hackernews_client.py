# 文件路径：src/hackernews_client.py

import requests  # 导入 requests 库用于发送 HTTP 请求
from bs4 import BeautifulSoup  # 导入 BeautifulSoup 库用于解析 HTML
from urllib.parse import urljoin  # 导入 urljoin 用于处理相对 URL

class HackerNewsClient:
    def __init__(self, base_url='https://news.ycombinator.com/'):
        """
        初始化 HackerNewsClient 类。
        :param base_url: Hacker News 网站的基本 URL，默认为 https://news.ycombinator.com/
        """
        self.base_url = base_url

    def fetch_top_stories(self, limit=10):
        """
        抓取 Hacker News 网站的头条新闻。
        :param limit: 要抓取的新闻数量，默认为 10 条
        :return: 已格式化的包含新闻标题和链接的字符串
        """
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
        for story in stories[:limit]:  # 限制返回的新闻数量
            title_tag = story.find('span', class_='titleline').find('a')
            if title_tag:
                title = title_tag.text  # 获取新闻标题
                link = title_tag['href']  # 获取新闻链接
                full_link = urljoin(self.base_url, link)  # 确保链接是完整的 URL
                formatted_stories.append(f"### {title}\nLink: {full_link}\n")

        # 将格式化的新闻条目合并为一个字符串返回
        return "\n".join(formatted_stories)

if __name__ == "__main__":
    # 测试 HackerNewsClient 类的功能
    client = HackerNewsClient()
    formatted_stories = client.fetch_top_stories()
    if formatted_stories:
        print(formatted_stories)
    else:
        print("No stories found.")
