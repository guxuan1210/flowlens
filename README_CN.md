# FlowLens：资金流向感知的多智能体市场情报系统

> 通过多智能体推理，帮助散户投资者解读市场叙事、风险信号和主力资金动向。
>
> 🚀 **Web 控制台**已上线，支持实时流式分析、人机协同审核、一键配置。

## 新闻
- [2026-05] **Web 控制台**发布 — React + FastAPI 全栈，WebSocket 实时推送，人机协同审核关卡，东方财富新闻源集成，主力资金分析师。
- [2026-05] **TradingAgents v0.2.5** — 落地版情绪分析师、GPT-5.5 等模型覆盖、Qwen/GLM/MiniMax 双区支持、环境变量配置、远程 Ollama、非美基准指数等。
- [2026-04] **TradingAgents v0.2.4** — 结构化输出 Agent、LangGraph 断点续跑、持久化决策日志、DeepSeek/Qwen/GLM/Azure 供应商支持、Docker 部署。
- [2026-03] **TradingAgents v0.2.3** — 多语言输出、GPT-5.4 系列模型、统一模型目录、回测日期保真、代理支持。

<div align="center">

🚀 [项目动机](#项目动机从机构ai到散户导向的市场情报) | ⚡ [安装与命令行](#安装与命令行) | 🖥️ [Web 控制台](#web-控制台) | 📦 [Python 调用](#python-调用) | 🤝 [参与贡献](#参与贡献) | 📄 [引用](#引用)

</div>

## 项目动机：从机构 AI 到散户导向的市场情报

大多数金融 AI 智能体是为机构工作流设计的：读财报、总结新闻、生成投资逻辑、辅助组合决策。这些能力有价值，但主要提升了本就资源充裕的市场参与者的决策效率。

FlowLens 的视角略有不同。它不只是为机构式决策构建 AI 助手，而是试图让机构级的市场情报对散户投资者更加可及、可解读。

在中国 A 股这样的市场，散户长期面临严重的信息不对称。公开新闻、K 线图、财务报表固然重要，但它们未必能揭示资金在市场趋势背后的真实动向。对散户来说，最重要的问题不只是"这家公司好不好"或者"新闻说了什么"，而是：

> 主力资金是在进场还是离场？

这就是 FlowLens 引入专门的**主力资金分析师**的原因。机构投资者的内部决策过程通常不透明、难以验证，但可观测的资金流向信号可以充当行为代理——包括主力资金净流入流出、大单和超大单净流向、板块资金轮动、以及北向资金动向。

通过将资金流向分析融入多智能体辩论和风控管线，FlowLens 帮助用户从基于叙事的分析转向基于行为的市场解读。目标不是预测或模仿机构决策，而是降低信息不对称，让资金动向更加透明，为散户和主力资金玩家之间创造更均衡的决策环境。

### 设计目标

1. **机构级推理**
   用专业智能体分析基本面、技术指标、新闻、情绪、风险和组合决策。

2. **散户友好的透明性**
   将复杂市场信号转化为个人投资者能理解和审核的报告。

3. **资金流向感知**
   整合主力资金流向、板块轮动和北向资金信号，帮助用户理解散户与主力资金的博弈格局。

---

平台部署了多个专业 LLM 智能体——从基本面分析师、情绪分析师、技术分析师，到交易员、风控团队和操纵检测器——协同评估市场状况，通过结构化辩论得出最优策略。

## Agent 团队

### 分析师团队
- **市场分析师**：使用 MACD、RSI 等技术指标检测模式、预测价格走势。
- **情绪分析师**：汇总新闻头条和社交媒体讨论，判断短期市场情绪。
- **新闻分析师**：监控全球新闻和宏观经济指标，解读事件对市场的影响。
- **基本面分析师**：评估公司财务、资产负债表和现金流，识别内在价值和潜在风险。
- **主力资金分析师**：追踪机构资金——主力资金流向、板块轮动和北向资金。回答图表无法回答的问题：*"大资金在买还是在卖？"* 使用 AKShare 和 Tushare 数据，挖掘纯价格分析会遗漏的聪明钱信号。

### 研究员团队
多头和空头研究员对分析师团队的成果进行严格审视。通过结构化辩论，平衡潜在收益与内在风险。

### 交易员 Agent
将分析师和研究员的研究成果组合成具体的交易方案，包含进出场时机和仓位规模。

### 风控管理与投资组合经理
- **风控团队**（激进、中性、保守三位分析师）从多角度辩论组合风险，评估波动率、流动性和尾部风险。
- **投资组合经理**综合所有前置工作，产出最终交易决策（强烈买入/买入/持有/卖出/强烈卖出）。

### 操纵风险检测器
交叉核验所有分析师报告，检测潜在的市场操纵信号、矛盾叙事或协同信息操作，在决策提交前做最后一次完整性检查。

### 完整管线

```
分析师（市场 → 情绪 → 新闻 → 基本面 → 主力资金）
  → 多头研究员 ⇄ 空头研究员（结构化辩论）
    → 研究经理 → [人审关卡*]
      → 交易员
        → 激进 ⇄ 保守 ⇄ 中性（风控辩论）
          → 投资组合经理 → [人审关卡*]
            → 操纵风险检测器 → 最终决策
```

*\*人审关卡可选，每次分析可独立开关。*

## 与原版 TradingAgents 的区别

本项目基于 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) 构建，聚焦于实际可用性、中国市场深度和人机协同。

| 维度 | 原版 TradingAgents | 本项目新增 |
|------|-------------------|-----------|
| **交互界面** | 纯命令行（终端向导） | Web 控制台——浏览器中启动分析、实时观看、浏览历史 |
| **分析师** | 4 个（市场、情绪、新闻、基本面） | **+ 主力资金分析师**（主力资金、板块轮动、北向资金） |
| **智能体** | 多空研究员、交易员、3 位风控、投资组合经理 | **+ 操纵风险检测器**（交叉验证完整性检查） |
| **人机交互** | 全自动，无法干预 | **人机协同审核**——在研究经理或投资组合经理处暂停，批准或带反馈修改 |
| **中国市场** | 有限（yfinance 对中国覆盖差） | **A 股一等支持**：东方财富新闻、财新、AKShare 数据、资金流向追踪 |
| **新闻来源** | yfinance + Alpha Vantage | **+ AKShare + 东方财富**，自动降级回退链路 |
| **流式输出** | 终端 Live 布局 | **WebSocket 实时**——每个 Agent 的输出实时生成就实时显示 |
| **配置方式** | 编辑代码中的 `DEFAULT_CONFIG` 或设环境变量 | **设置界面**——浏览器中切换 LLM、模型、辩论深度、数据源、人审关卡 |
| **管线可视化** | 终端进度条 | **阶段追踪**——清楚知道当前处于哪个阶段（分析师→研究→交易→风控→决策） |
| **决策历史** | 追加式 Markdown 日志 | 控制台中浏览历史运行记录和完整决策链路 |

一句话总结：原版是强大的研究框架，本项目给它加了可用的界面、中国市场的资金流向情报、以及在关键决策环节让人介入的能力。

## Web 控制台

FlowLens 配备完整的 Web 控制台，用于可视化分析管理。

```bash
# 启动后端
python -m dashboard.api.app

# 启动前端（另开终端）
cd dashboard/frontend
npm install
npm run dev
```

### 功能
- **实时流式输出**：分析运行时通过 WebSocket 实时观看每个 Agent 的输出逐字生成
- **管线可视化**：追踪分析所处的阶段（分析师 → 研究 → 交易 → 风控 → 决策）
- **人机协同审核**：可选择在关键决策点（研究经理、投资组合经理）暂停，审核、批准或带反馈修改 AI 输出
- **一键配置**：浏览器中配置 LLM 供应商、模型、研究深度、数据源和审核关卡
- **分析历史**：浏览过往运行记录和完整决策链路
- **多语言输出**：支持英文、中文、日文、韩文等

### 人机协同审核

启用后，管线在两个关键检查点暂停：

| 关卡 | 审核内容 | 可执行操作 |
|------|---------|-----------|
| **研究经理** | 多空辩论综合投资方案 | 批准，或带反馈意见修改 |
| **投资组合经理** | 最终交易决策和风险评估 | 批准，或覆盖评级，或提供反馈 |

你的反馈会被注入到后续节点，下游 Agent 能看到并回应。功能在每次分析运行中可独立开关——需要把关时打开，全自动运行时关闭。

### 中国国内市场支持（A 股）

FlowLens 对中国市场有一等支持，远不止表面的新闻翻译。

**资金流向是核心差异点。** 在 A 股市场，最重要的信号是资金流向——机构资金在往哪儿走。大多数海外工具对此完全盲视。FlowLens 整合了：

- **主力资金分析**：实时追踪主力资金流向（大单/超大单净流入）、机构 vs 散户资金对比、板块资金轮动。使用 AKShare 的个股资金流接口和 Tushare 资金流 API。
- **板块资金流向分析**：识别哪些行业板块正在吸引或流失机构资金，在价格变动之前捕捉轮动信号。
- **北向资金**：追踪通过沪深港通流入 A 股的外资——这是中国交易员密切关注的先行指标。

**真正有用的中文新闻源：**
- **东方财富**：中国最大的散户投资者平台。个股新闻和市场综合头条。
- **财新**：权威财经报道，通过 AKShare 桥接。
- **AKShare**：A 股原生的价格、基本面和资金流数据。

## 安装与命令行

### 安装

```bash
git clone https://github.com/guxuan1210/flowlens.git
cd flowlens
```

创建虚拟环境：
```bash
conda create -n tradingagents python=3.13
conda activate tradingagents
```

安装：
```bash
pip install .
```

### Docker

```bash
cp .env.example .env  # 填入你的 API 密钥
docker compose run --rm tradingagents
```

使用本地模型（Ollama）：
```bash
docker compose --profile ollama run --rm tradingagents-ollama
```

### 所需 API 密钥

为所选 LLM 供应商设置 API 密钥：

```bash
export OPENAI_API_KEY=...          # OpenAI (GPT)
export GOOGLE_API_KEY=...          # Google (Gemini)
export ANTHROPIC_API_KEY=...       # Anthropic (Claude)
export XAI_API_KEY=...             # xAI (Grok)
export DEEPSEEK_API_KEY=...        # DeepSeek
export DASHSCOPE_API_KEY=...       # 通义千问 — 国际版
export DASHSCOPE_CN_API_KEY=...    # 通义千问 — 中国版
export ZHIPU_API_KEY=...           # 智谱 GLM（国际）
export ZHIPU_CN_API_KEY=...        # 智谱 GLM（中国，open.bigmodel.cn）
export MINIMAX_API_KEY=...         # MiniMax — 全球
export MINIMAX_CN_API_KEY=...      # MiniMax — 中国
export OPENROUTER_API_KEY=...      # OpenRouter
export ALPHA_VANTAGE_API_KEY=...   # Alpha Vantage（数据供应商）
export TUSHARE_TOKEN=...           # Tushare（A股资金流向）
```

### 命令行使用

```bash
tradingagents          # 交互式向导
tradingagents analyze  # 跳过向导，直接开始分析

# 断点续跑
tradingagents analyze --checkpoint
tradingagents analyze --clear-checkpoints
```

## Python 调用

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"
config["deep_think_llm"] = "gpt-5.4"
config["quick_think_llm"] = "gpt-5.4-mini"
config["max_debate_rounds"] = 2

ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("NVDA", "2026-01-15")
print(decision)
```

### 主要配置项

完整配置见 `tradingagents/default_config.py`。关键设置：

| 配置项 | 说明 | 默认值 |
|-------|------|--------|
| `llm_provider` | LLM 供应商 | `"openai"` |
| `deep_think_llm` / `quick_think_llm` | 模型选择 | `"gpt-5.4"` / `"gpt-5.4-mini"` |
| `max_debate_rounds` | 多空辩论深度 | `1` |
| `max_risk_discuss_rounds` | 风控辩论深度 | `1` |
| `analyst_concurrency_limit` | 并行分析师数 | `1` |
| `output_language` | 报告语言 | `"English"` |
| `data_vendors` | 各类数据源 | yfinance |
| `enable_human_review` | 人机协同审核 | `False` |
| `human_review_points` | 启用的审核关卡 | `["research_manager", "portfolio_manager"]` |
| `checkpoint_enabled` | LangGraph 断点续跑 | `False` |

### 数据供应商

多供应商数据层，支持自动降级回退：

| 数据类别 | 可用供应商 |
|---------|-----------|
| 核心行情 | yfinance、Alpha Vantage |
| 技术指标 | yfinance、Alpha Vantage |
| 基本面数据 | yfinance、Alpha Vantage |
| 新闻 | yfinance、Alpha Vantage、AKShare、东方财富 |
| 资金流向 | AKShare、Tushare |

## 持久化与恢复

### 决策日志

始终开启。每次完成的运行将决策追加到 `~/.tradingagents/memory/trading_memory.md`。下次对同一股票运行时，系统获取已实现收益（原始收益和相对基准的 Alpha），生成一段反思，并将最近的同股票决策和跨股票经验注入到投资组合经理的提示词中。

### 断点续跑

通过 `--checkpoint` 或 `checkpoint_enabled: True` 选择性开启。LangGraph 在每个节点后保存状态，崩溃或中断的运行可从上一个成功步骤恢复，无需重新开始。成功完成后自动清理检查点。

## 参与贡献

欢迎社区贡献！无论是修 bug、改进文档还是提议新功能，你的参与都能让这个项目变得更好。加入我们的开源金融 AI 研究社区 [Tauric Research](https://tauric.ai/)。

## 引用

如果你的工作受益于 TradingAgents，请引用我们的论文：

```bibtex
@misc{xiao2025tradingagentsmultiagentsllmfinancial,
      title={TradingAgents: Multi-Agents LLM Financial Trading Framework}, 
      author={Yijia Xiao and Edward Sun and Di Luo and Wei Wang},
      year={2025},
      eprint={2412.20138},
      archivePrefix={arXiv},
      primaryClass={q-fin.TR},
      url={https://arxiv.org/abs/2412.20138}, 
}
```
