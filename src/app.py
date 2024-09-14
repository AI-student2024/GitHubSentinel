from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os

from config import Config
from github_client import GitHubClient
from hacker_news_client import HackerNewsClient
from report_generator import ReportGenerator
from llm import LLM
from logger import LOG
from bidder_client import BidderClient, ProjectQueryParams  # 招标信息的客户端
from subscription_manager import SubscriptionManager

app = Flask(__name__)
CORS(app)

# 初始化配置
config = Config()

# 初始化日志
LOG.info("应用程序启动，加载配置")

# 初始化 BidderClient
bidder_client = BidderClient(config)

@app.route('/generate_subscriptions_report', methods=['POST'])
def generate_subscriptions_report():
    data = request.json
    model_type = data.get('model_type')
    model_name = data.get('model_name')
    days = data.get('days', 1)

    if not model_type or not model_name:
        return jsonify({'error': '缺少必要的参数'}), 400

    try:
        llm, report_generator = get_llm_and_report_generator(model_type, model_name)
        github_client = GitHubClient(config.github_token)
        subscription_manager = SubscriptionManager(config.subscriptions_file)

        subscriptions = subscription_manager.list_subscriptions()

        reports = {}
        for repo in subscriptions:
            markdown_file_path = github_client.export_progress_by_date_range(repo, int(days))
            report, report_file_path = report_generator.generate_github_report(markdown_file_path)
            reports[repo] = {'report': report, 'file_path': report_file_path}

        return jsonify({'reports': reports})
    except Exception as e:
        LOG.error(f"生成订阅报告时发生错误：{e}")
        return jsonify({'error': str(e)}), 500


def get_llm_and_report_generator(model_type, model_name):
    config.llm_model_type = model_type
    if model_type == "openai":
        config.openai_model_name = model_name
    elif model_type == "ollama":
        config.ollama_model_name = model_name
    else:
        LOG.error(f"不支持的模型类型: {model_type}")
        raise ValueError(f"不支持的模型类型: {model_type}")
    
    llm = LLM(config)
    report_generator = ReportGenerator(llm, config.report_types)
    return llm, report_generator


@app.route('/generate_github_report', methods=['POST'])
def generate_github_report():
    data = request.json
    repo = data.get('repo')
    days = data.get('days', 1)
    model_type = data.get('model_type')
    model_name = data.get('model_name')

    if not repo or not model_type or not model_name:
        return jsonify({'error': '缺少必要的参数'}), 400

    try:
        llm, report_generator = get_llm_and_report_generator(model_type, model_name)
        github_client = GitHubClient(config.github_token)

        markdown_file_path = github_client.export_progress_by_date_range(repo, int(days))
        report, report_file_path = report_generator.generate_github_report(markdown_file_path)

        return jsonify({'report': report, 'file_path': report_file_path})
    except Exception as e:
        LOG.error(f"生成 GitHub 报告时发生错误：{e}")
        return jsonify({'error': str(e)}), 500


@app.route('/generate_hn_topic_report', methods=['POST'])
def generate_hn_topic_report():
    data = request.json
    date = data.get('date')
    hour = data.get('hour')
    model_type = data.get('model_type')
    model_name = data.get('model_name')

    if not model_type or not model_name:
        return jsonify({'error': '缺少必要的参数'}), 400

    try:
        llm, report_generator = get_llm_and_report_generator(model_type, model_name)
        hn_client = HackerNewsClient()

        markdown_file_path = hn_client.export_top_stories(date, hour)
        report, report_file_path = report_generator.generate_hn_topic_report(markdown_file_path)

        return jsonify({'report': report, 'file_path': report_file_path})
    except Exception as e:
        LOG.error(f"生成 Hacker News 主题报告时发生错误：{e}")
        return jsonify({'error': str(e)}), 500


@app.route('/generate_hn_daily_report', methods=['POST'])
def generate_hn_daily_report():
    data = request.json
    date = data.get('date')
    model_type = data.get('model_type')
    model_name = data.get('model_name')

    if not date or not model_type or not model_name:
        return jsonify({'error': '缺少必要的参数'}), 400

    try:
        llm, report_generator = get_llm_and_report_generator(model_type, model_name)
        directory_path = os.path.join('hacker_news', date)

        report, report_file_path = report_generator.generate_hn_daily_report(directory_path)

        return jsonify({'report': report, 'file_path': report_file_path})
    except Exception as e:
        LOG.error(f"生成 Hacker News 每日汇总报告时发生错误：{e}")
        return jsonify({'error': str(e)}), 500


@app.route('/generate_bidder_list_report', methods=['POST'])
def generate_bidder_list_report():
    data = request.json
    model_type = data['model_type']
    model_name = data['model_name']
    start_date = data['start_date']
    end_date = data['end_date']
    keywords = data['keywords']

    try:
        llm, report_generator = get_llm_and_report_generator(model_type, model_name)

        query_params = ProjectQueryParams(
            start_date=start_date,
            end_date=end_date,
            keyword=keywords,
            class_id="1",
            search_mode="1",
            search_type="1",
            page_index="1",
            page_size="5",
            province_code="0",
            city_code=""
        )

        # 使用 bidder_client 查询项目列表
        projects, raw_file_path = bidder_client.query_project_list(query_params)
        
        if not projects:
            return jsonify({'error': '未查询到任何项目'}), 404

        report, report_file_path = report_generator.generate_bidder_list_report(raw_file_path)

        response = {
            'report': report,
            'file_path': report_file_path
        }
        return jsonify(response)

    except Exception as e:
        LOG.error(f"生成招标项目列表报告时发生错误：{e}")
        return jsonify({'error': str(e)}), 500


@app.route('/download_report', methods=['GET'])
def download_report():
    file_path = request.args.get('file_path')
    if file_path and os.path.exists(file_path):
        try:
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            LOG.error(f"下载报告时发生错误：{e}")
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': '文件未找到'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
