# GitHub Sentinel

<p align="center">
    <br> <a href="README.md">中文</a> | English
</p>

GitHub Sentinel is an open-source AI-powered tool designed for developers and project managers. It automatically retrieves and summarizes updates from subscribed GitHub repositories on a daily/weekly basis. The main features include subscription management, update retrieval, notification system, and report generation.

## Features
- Subscription Management
- Update Retrieval
- Notification System
- Report Generation
- **Hacker News Reports**: Generates daily technology trend reports and sends notifications

## Quick Start

### 1. Install Dependencies

First, install the required dependencies:

```sh
pip install -r requirements.txt
```

### 2. Configure the Application

Edit the `config.json` file to set your GitHub Token, Email settings (example with Tencent Enterprise Email), subscription file, and update settings:

```json
{
    "github_token": "your_github_token",
    "email":  {
        "smtp_server": "smtp.exmail.qq.com",
        "smtp_port": 465,
        "from": "from_email@example.com",
        "password": "your_email_password",
        "to": "to_email@example.com"
    },
    "slack_webhook_url": "your_slack_webhook_url",
    "subscriptions_file": "subscriptions.json",
    "github_progress_frequency_days": 1,
    "github_progress_execution_time":"08:00",
    "hackernews_frequency_days": 1,
    "hackernews_execution_time": "08:00"
}
```

**For security reasons:** It is recommended to configure GitHub Token and Email Password using environment variables to avoid storing sensitive information in plain text, as shown below:

```shell
# GitHub
export GITHUB_TOKEN="github_pat_xxx"
# Email
export EMAIL_PASSWORD="password"
```

### 3. How to Run

GitHub Sentinel supports three running modes:

#### A. Running as a Command-Line Tool

You can run the application interactively from the command line:

```sh
python src/command_tool.py
```

In this mode, you can manually input commands to manage subscriptions, retrieve updates, and generate reports.

#### B. Running as a Background Service

To run the application as a background service (daemon), it will automatically update according to the relevant configuration on a regular basis.

You can directly use the daemon management script [daemon_control.sh](daemon_control.sh) to start, check status, stop, and restart:

1. Start the service:

    ```sh
    ./daemon_control.sh start
    Starting DaemonProcess...
    DaemonProcess started.
    ```

   - This will start `./src/daemon_process.py`, generating reports and sending emails regularly according to the update frequency and timing set in `config.json`.
   - The logs for this service will be saved to the `logs/DaemonProcess.log` file. At the same time, cumulative historical logs will be appended to the `logs/app.log` log file.

2. Check service status:

    ```sh
    ./daemon_control.sh status
    DaemonProcess is running.
    ```

3. Stop the service:

    ```sh
    ./daemon_control.sh stop
    Stopping DaemonProcess...
    DaemonProcess stopped.
    ```

4. Restart the service:

    ```sh
    ./daemon_control.sh restart
    Stopping DaemonProcess...
    DaemonProcess stopped.
    Starting DaemonProcess...
    DaemonProcess started.
    ```

#### C. Running as a Gradio Server

To run the application using the Gradio interface, which allows users to interact with the tool via a web interface:

```sh
python src/gradio_server.py
```

- This will start a web server on your machine, allowing you to manage subscriptions and generate reports through a user-friendly interface.
- By default, the Gradio server will be accessible at `http://localhost:7860`, but you can share it publicly if needed.

