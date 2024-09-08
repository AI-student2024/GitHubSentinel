import requests
import os
from datetime import datetime
from dataclasses import dataclass
from logger import LOG  # 导入日志模块

@dataclass
class ProjectQueryParams:
    """
    用于存储项目查询参数的数据类
    """
    start_date: str
    end_date: str
    keyword: str
    class_id: str
    search_mode: str
    search_type: str
    page_index: str
    page_size: str
    province_code: str
    city_code: str

@dataclass
class Project:
    """
    用于存储单个项目信息的数据类
    """
    project_id: str
    publish_time: str
    title: str

class BidderClient:
    def __init__(self, config):
        """
        初始化 BidderClient 类，设置 API 基础 URL 和请求头部
        """
        self.config = config
        print(f"Config Bidder API Key: {config.bidder_api_key}")  # 调试输出
        self.api_key = os.getenv('BID_TOKEN', config.bidder_api_key)
        self.base_url = config.bidder_base_url
        self.headers = {
            "X-APISpace-Token":self.api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def fetch_api_data(self, endpoint, payload):
        """
        通用的API数据获取方法，负责发送请求并返回数据。
        """
        url = self.base_url + endpoint
        LOG.info(f"发送请求到 {url}")
        response = requests.post(url, data=payload, headers=self.headers)
        
        if response.status_code == 200:  # 请求成功
            response_data = response.json()
            if response_data.get("code") == 200:  # API 返回成功码
                LOG.info(f"API请求成功，返回数据: {response_data}")
                return response_data.get("data", {})
            else:  # API 返回错误信息
                LOG.error(f"API返回错误，code: {response_data.get('code')}, 错误信息: {response_data.get('msg')}")
        else:  # 请求失败
            LOG.error(f"请求失败，状态码: {response.status_code}, 错误信息: {response.text}")
        
        return None

    def query_project_list(self, query_params: ProjectQueryParams):
        """
        查询项目列表，返回包含项目信息的对象列表，并生成 Markdown 文件。
        """
        LOG.info(f"正在查询项目列表... 关键词: {query_params.keyword}, 查询时间范围: {query_params.start_date} 至 {query_params.end_date}")
        
        # 手动将数据类属性名映射到 API 要求的 key 名
        payload = {
            "startDate": query_params.start_date,
            "endDate": query_params.end_date,
            "keyword": query_params.keyword,
            "classId": query_params.class_id,
            "searchMode": query_params.search_mode,
            "searchType": query_params.search_type,
            "pageIndex": query_params.page_index,
            "pageSize": query_params.page_size,
            "proviceCode": query_params.province_code,
            "cityCode": query_params.city_code
        }

        # 使用通用的API获取方法查询项目列表
        project_list_data = self.fetch_api_data("project-list", payload)

        # 打印返回的数据类型及内容，便于调试
        LOG.info(f"fetch_api_data 返回数据类型: {type(project_list_data)}")
        LOG.info(f"fetch_api_data 返回数据内容: {project_list_data}")
        
        if not project_list_data:
            LOG.error("未能获取项目列表。")
            return None

        # 检查是否为字典并进行处理
        if isinstance(project_list_data, dict):
            LOG.info(f"转换前的项目列表数据: {project_list_data.get('data', [])}")
            project_data = project_list_data.get('data', [])
        elif isinstance(project_list_data, list):
            LOG.info(f"转换前的项目列表数据: {project_list_data}")
            project_data = project_list_data
        else:
            LOG.error("项目列表数据格式无效。")
            return None

        # 生成 Project 对象列表，包含项目 id 和发布时间
        projects = []
        md_content = f"# 项目列表 ({query_params.start_date} - {query_params.end_date})\n\n"
        for project in project_data:  # 这里使用 project_data 来生成项目列表
            projects.append(Project(
                project_id=project.get('id', '无ID'),
                publish_time=project.get('publish', '无发布时间'),
                title=project.get('title', '无标题')
            ))
            # 生成 Markdown 内容
            md_content += f"## title: {project.get('title', '无标题')}\n"
            md_content += f"- **id**: {project.get('id', '无ID')}\n"
            md_content += f"- **newsTypeID**: {project.get('newsTypeID', '无类型')}\n"
            md_content += f"- **publish**: {project.get('publish', '无发布时间')}\n"
            md_content += f"- **proviceCode**: {project.get('proviceCode', '无省编码')}\n"
            md_content += f"- **cityCode**: {project.get('cityCode', '无市编码')}\n"
            md_content += "---\n"
        
        # 保存项目列表为 Markdown 文件
        current_date = datetime.now().strftime("%Y%m%d")
        filename = f"bidder_list_{query_params.start_date}_to_{query_params.end_date}_{current_date}.md"
        file_path = self.save_md_file(md_content, filename)
        LOG.info(f"项目列表已保存至: {file_path}")
        
        return projects, file_path  # 返回包含项目信息的对象列表

    def query_project_full_details(self, project: Project):
        """
        查询项目的详细信息，包含项目详情和结构化数据，并生成 Markdown 文件
        """
        LOG.info(f"正在查询项目的详细信息... 项目ID: {project.project_id}, 发布时间: {project.publish_time}")
        
        # 构建查询详情的请求体
        payload = {
            "publishTime": project.publish_time,
            "id": project.project_id
        }
        
        # 获取项目详情
        project_details_data = self.fetch_api_data("get-project", payload)
        if not project_details_data:
            LOG.error("未能获取项目详情。")
            return None
        
        # 获取项目结构化数据
        project_structured_data = self.fetch_api_data("getDetail", payload)
        if not project_structured_data:
            LOG.error("未能获取项目结构化数据。")
            return None
        
        # 整合项目详情和项目结构化数据
        LOG.info("正在整合项目详情和结构化数据。")
        
        # 将项目详情和结构化数据转换为 Markdown 格式
        md_content = f"# 项目详细信息\n\n"
        
        # 添加项目详情部分
        md_content += "## 项目详情\n\n"
        md_content += self.dict_to_markdown(project_details_data)
        
        # 添加项目结构化数据部分
        md_content += "\n## 项目结构化数据\n\n"
        md_content += self.dict_to_markdown(project_structured_data)
        
        LOG.info("项目详细信息查询完成，返回Markdown内容。")

        # 生成文件路径，并保存为 Markdown 文件
        current_date = datetime.now().strftime("%Y%m%d")
        filename = f"bidder_details_{project.project_id}_{current_date}.md"
        file_path = self.save_md_file(md_content, filename)

        return file_path

    # Helper function to save Markdown content to file
    def save_md_file(self, content, filename):
        """
        将生成的 Markdown 内容保存到指定文件，并返回文件路径
        """
        # 确保目录 bid_info 存在，与 src 同级
        dir_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bid_info")
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            LOG.info(f"创建目录: {dir_path}")
        
        # 保存文件
        file_path = os.path.join(dir_path, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        LOG.info(f"文件已保存: {file_path}")
        return file_path

    # Helper function to convert dict to markdown format
    def dict_to_markdown(self, data, indent=0):
        """
        将字典数据递归转换为 Markdown 格式
        """
        md_content = ""
        for key, value in data.items():
            # 添加缩进和键值对
            md_content += " " * indent + f"**{key}**: "
            # 如果值是字典，递归处理
            if isinstance(value, dict):
                md_content += "\n" + self.dict_to_markdown(value, indent + 2)
            # 如果值是列表，列出所有项
            elif isinstance(value, list):
                md_content += "\n"
                for item in value:
                    md_content += " " * (indent + 2) + f"- {item}\n"
            else:
                # 普通值直接写入
                md_content += f"{value}\n"
        return md_content



if __name__ == "__main__":

  # 创建 BidderClient 实例
  from config import Config
  config = Config()
  bidder_client = BidderClient(config)
   
  # 构建查询参数
  query_params = ProjectQueryParams(
    start_date="2024-08-01",  # 查询的开始日期
    end_date="2024-09-01",    # 查询的结束日期
    keyword="数据中心",           # 查询的关键词
    class_id="1",             # 项目类别 ID
    search_mode="1",          # 查询模式
    search_type="1",          # 查询类型
    page_index="1",           # 页码
    page_size="5",            # 每页项目数量
    province_code="0",        # 省份编码
    city_code=""              # 城市编码
    )

  # 查询项目列表
  projects,file_path = bidder_client.query_project_list(query_params)

  # 检查是否有项目返回
  if projects:
    
     # 输出项目的基本信息
     print("\n查询到以下项目：\n")
     for project in projects:
         print(f"项目ID: {project.project_id}, 项目标题: {project.title}, 发布时间: {project.publish_time}")

     # 选择其中一个项目查询详细信息
     selected_project = projects[0]  # 示例中选择第一个项目
     print(f"\n正在获取项目 '{selected_project.title}' 的详细信息...\n")
    
     # 查询项目的详细信息并保存为 Markdown 文件
     project_details_file = bidder_client.query_project_full_details(selected_project)

     # 打印保存的 Markdown 文件路径
     if project_details_file:
         print(f"项目详细信息已保存至: {project_details_file}")
     else:
         print("获取项目详细信息失败。")
  else:
       print("未查询到项目。")