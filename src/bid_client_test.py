import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
from logger import LOG
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
}

# 从指定URL抓取并解析页面，提取符合关键词的条目
def fetch_and_parse(url, keywords, max_items=30):
    LOG.info(f"开始从URL {url} 抓取招标信息，关键词: {keywords}")
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        LOG.debug(f"网页内容: {soup.prettify()}")  # 输出网页内容进行调试
    except Exception as e:
        LOG.error(f"抓取URL {url} 时出现错误: {e}")
        return []

    items = []
    try:
        # 每个招标条目在 'li' 标签下，类名为 'vT-srch-result-list-bid'
        for item in soup.find_all('li', class_='vT-srch-result-list-bid'):
            if len(items) >= max_items:
                break
            # 抓取标题和链接
            title_tag = item.find('a')
            title = title_tag.text.strip()
            link = title_tag['href']
            
            # 抓取发布日期
            date = item.find('span', class_='text-gray').text.strip()
            
            # 过滤关键词
            if any(keyword.lower() in title.lower() for keyword in keywords):
                items.append((date, title, link))
        
        # 按日期排序
        items.sort(key=lambda x: x[0])
        LOG.info(f"成功解析到 {len(items)} 条符合条件的招标项目")
        
    except Exception as e:
        LOG.error(f"解析页面时出现错误: {e}")
    
    return items

def main():
    test_url = 'https://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=1&timeType=2&searchchannel=0&kw=&bidSort=0&pinMu=0&bidType=0'
    keywords = ['智慧园区']

    # 为了避免频繁访问限制，设置访问间隔时间
    time.sleep(10)
    
    items = fetch_and_parse(test_url, keywords, max_items=30)

    if items:
        LOG.info(f"找到 {len(items)} 条招标信息")
    else:
        LOG.warning("未找到符合条件的招标信息")

if __name__ == "__main__":
    main()
