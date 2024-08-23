import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)

def export_progress_by_date_range(repo, days):
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径

    return report, report_file_path  # 返回报告内容和报告文件路径

# 创建Gradio界面
"""
demo = gr.Interface(
    fn=export_progress_by_date_range,  # 指定界面调用的函数
    title="GitHubSentinel",  # 设置界面标题
    submit_btn="生成报告",  # 设置提交按钮的文本
    clear_btn="重置条件",  # 设置重置按钮的文本
    inputs=[
        gr.Dropdown(
            subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目"
        ),  # 下拉菜单选择订阅的GitHub项目
        gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期", info="生成项目过去一段时间进展，单位：天"),
        # 滑动条选择报告的时间范围
    ],
    outputs=[gr.Markdown(), gr.File(label="下载报告")],  # 输出格式：Markdown文本和文件下载
)
"""
# 优化Gradio界面：改为上下布局，并添加更多说明
def clear_inputs():
    return "", "2天"  # 重置为默认值

def process_days(days):
    return int(days[0])  # 提取并转换为整数

# 自定义CSS样式，增加说明文字和Markdown区域的边框
css = """
#report_output {
    border: 1px solid #ccc;
    padding: 10px;
    border-radius: 5px;
    background-color: #f9f9f9;
}
#description {
    font-size: 14px;
    color: #555;
}
"""

# 创建Gradio界面
with gr.Blocks(css=css) as demo:
    gr.Markdown("# GitHubSentinel")
    
    # 添加描述
    gr.Markdown(
        "### 订阅您的GitHub项目并选择报告周期，然后点击生成报告。"
        "报告将展示项目的主要进展和文件，您可以下载并查看详细内容。", 
        elem_id="description"
    )
    
    with gr.Column():
        repo = gr.Dropdown(
            subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目"
        )
        days = gr.Radio(
            choices=["1天", "2天", "3天", "4天", "5天", "6天", "7天"], 
            value="2天",  # 默认选择2天
            label="报告周期",
            info="请选择报告周期，单位：天"
        )
        
        with gr.Row():  # 将按钮放在同一行
            generate_btn = gr.Button(value="生成报告", variant="primary")
            reset_btn = gr.Button(value="重置条件", variant="secondary")
        
        report_output = gr.Markdown(elem_id="report_output")
        file_output = gr.File(label="下载报告")

        generate_btn.click(
            fn=lambda repo, days: export_progress_by_date_range(repo, process_days(days)), 
            inputs=[repo, days], 
            outputs=[report_output, file_output]
        )
        reset_btn.click(clear_inputs, outputs=[repo, days])


if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")  # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))