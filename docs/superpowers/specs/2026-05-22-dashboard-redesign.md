# TradingAgents Dashboard 交互式 Web 界面设计

## Context

TradingAgents 是一个 LangGraph 多智能体交易分析框架，已有 CLI 交互界面但缺乏专业的 Web 前端。项目 `dashboard/` 目录包含 FastAPI 后端 + React 前端基础框架（WebSocket 流式、Zustand 状态管理、路由），但前端实现简陋——安装了 Radix UI、Recharts、react-markdown 却未使用。本次设计将这些能力整合到专业金融分析面板中。

## Design Decisions

| 维度 | 决策 |
|------|------|
| 技术方案 | 增强现有 FastAPI + React 前端（不复刻 gradio/htmx） |
| 页面布局 | 卡片网格，每个 Agent 一张独立卡片 |
| 视觉风格 | 深色专业风 Dark Navy — Tailwind `slate-900` 底 + `sky-400`/`violet-400` 强调色 |
| 配置表单 | 两栏：左侧配置面板 + 右侧实时预览 |
| 卡片交互 | 状态灯（绿/蓝/灰）+ 脉冲呼吸动画 + 点击 Dialog 展开完整报告 |

## Pages

### 1. Dashboard (`/`)

- **Stats Row**: 3 张统计卡 — Total Analyses, Buy Signals, Sell Signals（从 history API 拉数据）
- **Performance Chart**: Recharts 柱状图，展示最近 N 次分析的收益/Alpha 分布
- **Recent Analyses**: 最近 5 条分析列表，每行可点击跳转到 Results Viewer
- **Empty State**: 无历史数据时引导用户创建第一次分析

### 2. Run Analysis (`/run`)

核心页面，承载三个阶段的切换：

**Phase A — Configuration（idle 状态）**:
- 左栏表单: Ticker 输入、Date picker、Analyst 复选框组（4个）、LLM Provider 下拉、Quick/Deep Model 下拉、Research Depth 按钮组、Output Language 输入
- 右栏预览: 实时摘要显示用户当前选择的参数 + Pipeline 预览图（4 analysts → 2 researchers → Trader → 3 risk → PM）

**Phase B — Streaming（running 状态）**:
- 顶部: 配置摘要折叠条 + Stop 按钮 + 实时计时器
- 中部: Agent 卡片网格（动态列数，4列展示 Analyst 阶段，3列展示 Risk 阶段）
  - 每张卡片: 彩色左边框 + 状态灯(绿/蓝脉冲/灰) + Agent 名称 + 缩略输出 + tool call 计数 + 耗时
  - 运行中卡片: CSS `@keyframes pulse` 呼吸动效，流式追加内容
  - 完成卡片: 绿色边框 + 绿光晕 `box-shadow`，可点击打开 Dialog 看完整报告
  - 等待卡片: 虚线边框 + opacity 降低
- 底部状态栏: LLM calls, Tool calls, Tokens (in/out), Elapsed time
- 左侧 Pipeline 进度指示器（5 阶段：Analysts → Research → Trader → Risk → Decision）

**Phase C — Completion（completed 状态）**:
- 全卡片变为绿色完成态
- 居中弹出 Rating 徽章（Buy=绿 Sell=红 Hold=黄），大字显示评级 + 置信度
- 1.5s 后自动跳转到 Results Viewer

**Phase D — Error**:
- 红色错误卡片，显示错误信息 + Try Again 按钮

### 3. Results Viewer (`/results/:ticker/:date`)

Tab 式布局（Radix Tabs），5 个标签页:

1. **Analyst Reports**: 4 个子区块，每个分析师的完整报告（markdown 渲染）
2. **Research Debate**: Bull vs Bear 辩论记录 + Research Manager 综合判断
3. **Trading Plan**: Trader 的交易提案（动作/价格/止损/仓位）
4. **Risk Analysis**: 激进/保守/中立三方辩论记录 + Portfolio Manager 最终决策
5. **Final Decision**: 评级大字 + 执行摘要 + 投资论点 + 目标价 + 时间范围

所有内容用 `react-markdown` + `rehype-highlight` 渲染，支持代码块语法高亮。

### 4. History (`/history`)

- 搜索栏: ticker 筛选输入 + 日期范围选择
- 数据表格: Ticker | Date | Rating(彩色标签) | Return | Alpha | Actions
- 点击行跳转到 Results Viewer
- 分页支持

### 5. Settings (`/settings`)

优化现有页面:
- 用 Radix Select 替换原生下拉
- 用 Radix Switch 替换复选框
- 分组用 Radix Accordion / 卡片 Section
- API Key 字段用密码输入 + 显示/隐藏切换

## Component Architecture

```
src/
  components/
    layout/
      Layout.tsx          # 已有，保留
      Sidebar.tsx          # 已有，优化 active 态样式
      Header.tsx           # 已有
    ui/
      AgentCard.tsx         # NEW: Agent 状态卡片（状态灯+脉冲+缩略输出）
      AgentCardGrid.tsx     # NEW: Agent 卡片网格容器
      PipelineProgress.tsx  # NEW: 5阶段 Pipeline 进度指示器
      RatingBadge.tsx       # NEW: Buy/Sell/Hold 评级徽章
      StatsBar.tsx          # NEW: LLM calls, tokens, time 底部状态栏
      MarkdownReport.tsx    # NEW: react-markdown 包装组件
      ConfigPreview.tsx     # NEW: 配置预览面板
      EmptyState.tsx        # NEW: 空状态引导
    charts/
      ReturnsChart.tsx      # NEW: Recharts 收益柱状图
      RatingPieChart.tsx    # NEW: Recharts 评级分布饼图
  pages/
    Dashboard.tsx     # 重写: 加 Recharts 图表
    RunAnalysis.tsx   # 重写: 卡片网格 + 3阶段切换
    ResultsViewer.tsx  # 重写: Radix Tabs + markdown 渲染
    History.tsx       # 优化: 搜索+表格
    Settings.tsx      # 优化: Radix UI 控件
  store/
    analysisStore.ts   # 保留并扩展: 添加 pipeline stage 跟踪
    configStore.ts     # 保留
  hooks/
    useWebSocket.ts    # NEW: WebSocket 连接 hook（封装 connect/disconnect/reconnect）
    useAnalysisStream.ts # NEW: 流式数据分析 hook（处理 WS 消息分发）
```

## Data Flow

```
[User fills form] → POST /api/analysis/run → {run_id, ws_url}
  → useWebSocket(ws_url) 建立连接
  → WS messages: agent_status | report_chunk | stats | completion | error
  → analysisStore 更新:
    - agentStatuses: Record<string, AgentStatus>
    - reportSections: Record<string, string>
    - stats: {llm_calls, tool_calls, tokens_in, tokens_out}
    - pipelineStage: 'analysts' | 'research' | 'trader' | 'risk' | 'decision'
  → AgentCardGrid 响应式渲染卡片
  → completion 时自动跳转 /results/:ticker/:date
```

## Visual Style Reference

- **Background**: `bg-slate-950` (page), `bg-slate-900` (cards)
- **Border**: `border-slate-800` (default), `border-sky-500/50` (active)
- **Accent colors per agent**:
  - Market Analyst: `sky-400`
  - Sentiment Analyst: `violet-400`
  - News Analyst: `emerald-400`
  - Fundamentals Analyst: `amber-400`
  - Bull Researcher: `green-500`
  - Bear Researcher: `red-400`
  - Trader: `cyan-400`
  - Risk (Aggressive/Conservative/Neutral): `pink-400`/`blue-400`/`slate-400`
  - Portfolio Manager: `sky-300`
- **Rating colors**: Buy=`#22c55e`, Overweight=`#84cc16`, Hold=`#eab308`, Underweight=`#f97316`, Sell=`#ef4444`
- **Typography**: 系统字体栈，报告区域用 `prose prose-invert`（Tailwind Typography）

## Card Animation Spec

```css
@keyframes agent-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.4); }
  50%      { box-shadow: 0 0 0 8px rgba(56, 189, 248, 0);   }
}
.card-running {
  animation: agent-pulse 2s ease-in-out infinite;
  border-color: #38bdf8; /* sky-400 */
}
.card-done {
  border-color: #22c55e; /* green-500 */
  box-shadow: 0 0 12px rgba(34, 197, 94, 0.15);
}
.card-pending {
  border-style: dashed;
  border-color: #334155; /* slate-700 */
  opacity: 0.5;
}
```

## Backend Changes

**Minimal changes needed** — 现有 API 已满足需求:

1. `analysis_runner.py`: 确保 `_handle_chunk()` 发送 pipeline stage 变化事件（当前仅发送 agent_status/report_chunk/stats，需增加 `pipeline_stage` 消息类型）
2. `websocket_manager.py`: cached state 增加 `pipeline_stage` 字段以支持 late-joiner
3. `schemas/streaming.py`: `WSMessageType` 枚举新增 `pipeline_stage`

## Verification

1. `cd dashboard/frontend && npm run dev` — 前端启动无报错，页面正常渲染
2. 访问 `/run` — 配置表单正常交互，选择 LLM provider 后模型下拉动态加载
3. 点击 Start Analysis — WebSocket 连接建立，卡片网格从 pending → running → done 状态正确切换，脉冲动画生效
4. 点击完成的 Agent 卡片 — Dialog 弹出完整 markdown 渲染报告
5. Analysis 完成后 — 自动跳转 Results Viewer，5 个 Tab 正常展示
6. `/history` — 搜索筛选正常，点击行跳转结果页
7. `/settings` — Radix UI 控件正常工作，配置持久化
8. `npm run build` — 生产构建成功
