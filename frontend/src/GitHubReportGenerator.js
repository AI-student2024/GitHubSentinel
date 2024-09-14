// src/GitHubReportGenerator.js

import React, { useState } from 'react';
import axios from 'axios';

function GitHubReportGenerator() {
  const [repo, setRepo] = useState('');
  const [days, setDays] = useState(1);
  const [modelType, setModelType] = useState('openai');
  const [modelName, setModelName] = useState('gpt-3.5-turbo');
  const [report, setReport] = useState('');
  const [filePath, setFilePath] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const generateReport = () => {
    setError('');
    setLoading(true);
    axios.post('/generate_github_report', {
      repo,
      days,
      model_type: modelType,
      model_name: modelName,
    })
    .then(response => {
      setReport(response.data.report);
      setFilePath(response.data.file_path);
    })
    .catch(error => {
      console.error('生成报告时出错：', error);
      setError(error.response?.data?.error || '生成报告失败，请稍后重试。');
    })
    .finally(() => {
      setLoading(false);
    });
  };

  return (
    <div>
      <h2>生成 GitHub 报告</h2>
      <div>
        <label>仓库名称：</label>
        <input type="text" value={repo} onChange={e => setRepo(e.target.value)} placeholder="username/repository" />
      </div>
      <div>
        <label>过去天数：</label>
        <input type="number" value={days} onChange={e => setDays(e.target.value)} min="1" />
      </div>
      <div>
        <label>模型类型：</label>
        <select value={modelType} onChange={e => setModelType(e.target.value)}>
          <option value="openai">OpenAI</option>
          <option value="ollama">Ollama</option>
        </select>
      </div>
      <div>
        <label>模型名称：</label>
        <input type="text" value={modelName} onChange={e => setModelName(e.target.value)} />
      </div>
      <button onClick={generateReport} disabled={loading}>生成报告</button>
      {loading && <div>报告生成中，请稍候...</div>}
      {error && <div style={{ color: 'red' }}>{error}</div>}
      {report && (
        <div>
          <h3>报告内容：</h3>
          <pre>{report}</pre>
          <a href={`/download_report?file_path=${encodeURIComponent(filePath)}`} target="_blank" rel="noopener noreferrer">
            下载报告
          </a>
        </div>
      )}
    </div>
  );
}

export default GitHubReportGenerator;
