// src/App.js

import React from 'react';
import GitHubReportGenerator from './GitHubReportGenerator';
import HackerNewsTopicReportGenerator from './HackerNewsTopicReportGenerator';
import HackerNewsDailyReportGenerator from './HackerNewsDailyReportGenerator';
import BidderListReportGenerator from './BidderListReportGenerator';
// 如果有招标项目详情报告组件，导入并使用

function App() {
  return (
    <div>
      <h1>报告生成器</h1>
      <GitHubReportGenerator />
      <HackerNewsTopicReportGenerator />
      <HackerNewsDailyReportGenerator />
      <BidderListReportGenerator />
      {/* 其他组件 */}
    </div>
  );
}

export default App;
