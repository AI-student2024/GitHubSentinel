import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# 添加 src 目录到模块搜索路径，以便可以导入 src 目录中的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from bidder_client import BidderClient, ProjectQueryParams, Project  # 导入 BidderClient 和 Project 类


class TestBidderClient(unittest.TestCase):

    @patch('bidder_client.requests.post')
    def setUp(self, mock_post):
        # 初始化配置和客户端
        self.mock_config = MagicMock()
        self.mock_config.bidder_api_key = "mock_api_key"
        self.mock_config.bidder_base_url = "https://mock-api.com/"
        self.client = BidderClient(self.mock_config)
        
        # 模拟项目查询参数
        self.query_params = ProjectQueryParams(
            start_date="2024-08-01",
            end_date="2024-09-01",
            keyword="数据中心",
            class_id="1",
            search_mode="1",
            search_type="1",
            page_index="1",
            page_size="5",
            province_code="0",
            city_code=""
        )

        # 模拟项目
        self.mock_project = Project(
            project_id="12345",
            publish_time="2024-08-01",
            title="Mock Project"
        )

    @patch('bidder_client.requests.post')
    def test_query_project_list_success(self, mock_post):
        # 设置模拟的API响应，确保返回的数据结构是字典
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "code": 200,
            "data": [{
                "id": "12345",
                "title": "Test Project",
                "publish": "2024-08-01 00:12:00",
                "newsTypeID": "100",
                "proviceCode": "01",
                "cityCode": "001"
            }]
        }

        # 调用查询项目列表方法
        result = self.client.query_project_list(self.query_params)
        
        # 判断返回结果是否为 None
        if result is None:
            self.fail("query_project_list should not return None in success case")
        
        projects, file_path = result
        
        # 断言返回项目正确
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].project_id, "12345")
        self.assertEqual(projects[0].title, "Test Project")

        # 断言文件路径不为空
        self.assertTrue(file_path.endswith(".md"))

    @patch('bidder_client.requests.post')
    def test_query_project_list_failure(self, mock_post):
        # 模拟API返回错误
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {
            "code": 400,
            "msg": "Invalid parameters"
        }

        # 调用查询项目列表方法
        result = self.client.query_project_list(self.query_params)

        # 断言返回None
        self.assertIsNone(result)

    @patch('bidder_client.requests.post')
    def test_query_project_full_details_success(self, mock_post):
        # 模拟项目详情 API 响应
        mock_post.side_effect = [
            MagicMock(status_code=200, json=MagicMock(return_value={"code": 200, "data": {"detail": "Project Details"}})),
            MagicMock(status_code=200, json=MagicMock(return_value={"code": 200, "data": {"structured": "Structured Data"}}))
        ]

        # 调用查询项目详情方法
        file_path = self.client.query_project_full_details(self.mock_project)
        
        # 断言文件路径不为空
        self.assertTrue(file_path.endswith(".md"))

    @patch('bidder_client.requests.post')
    def test_query_project_full_details_failure(self, mock_post):
        # 模拟项目详情 API 返回错误
        mock_post.side_effect = [
            MagicMock(status_code=400, json=MagicMock(return_value={"code": 400, "msg": "Error fetching project details"})),
            MagicMock(status_code=400, json=MagicMock(return_value={"code": 400, "msg": "Error fetching structured data"}))
        ]

        # 调用查询项目详情方法
        file_path = self.client.query_project_full_details(self.mock_project)

        # 断言返回None
        self.assertIsNone(file_path)

    @patch('os.makedirs')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_save_md_file(self, mock_open, mock_makedirs):
        # 调用保存文件方法
        content = "# Test Markdown"
        filename = "test_file.md"
        file_path = self.client.save_md_file(content, filename)

        # 断言文件路径正确
        self.assertTrue(file_path.endswith("test_file.md"))

        # 检查文件写入是否被调用
        mock_open.assert_called_with(os.path.join(os.path.dirname(os.path.dirname(__file__)), "bid_info", filename), "w", encoding="utf-8")

    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    def test_directory_creation(self, mock_exists, mock_makedirs):
        # 模拟不存在目录时调用查询项目列表
        self.client.save_md_file("# Test", "test_file.md")
        
        # 断言 makedirs 被调用
        mock_makedirs.assert_called()

if __name__ == '__main__':
    unittest.main()
