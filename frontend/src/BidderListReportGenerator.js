// src/BidderListReportGenerator.js

import React, { useState } from 'react';
import axios from 'axios';

function BidderListReportGenerator() {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [keywords, setKeywords] = useState('');
  const [modelType, setModelType] = useState('openai');
  const [modelName, setModelName] = useState('gpt-3.5-turbo');
  const [report, setReport] = useState('');
  const [filePath, setFilePath] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const generateReport = () => {
    setError('');
    setLoading(true);
    axios.post('/generate_bidder_list_report', {
      start_date: startDate,
      end_date: endDate,
      keywords,
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
      <h2>生成招标项目列表报告</h2>
      <div>
        <label>开始日期：</label>
        <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
      </div>
      <div>
        <label>结束日期：</label>
        <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
      </div>
      <div>
        <label>关键词：</label>
        <input type="text" value={keywords} onChange={e => setKeywords(e.target.value)} />
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

export default BidderListReportGenerator;
