import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '@/api/client'
import { useAnalysisStore } from '@/store/analysisStore'
import { ConfigPreview } from '@/components/ui/ConfigPreview'
import { AgentCardGrid } from '@/components/ui/AgentCardGrid'
import { PipelineProgress } from '@/components/ui/PipelineProgress'
import { StatsBar } from '@/components/ui/StatsBar'
import { RatingBadge } from '@/components/ui/RatingBadge'
import type { AnalysisParams, AnalysisRunResponse } from '@/types/analysis'
import type { ProviderInfo, ModelOptions } from '@/types/config'
import type { WSMessage, AgentStatus } from '@/types/streaming'
import { Play, CheckCircle2, XCircle } from 'lucide-react'

const ANALYST_OPTIONS = [
  { key: 'market', label: 'Market Analyst', desc: 'Technical indicators, price data' },
  { key: 'social', label: 'Sentiment Analyst', desc: 'News, StockTwits, Reddit sentiment' },
  { key: 'news', label: 'News Analyst', desc: 'Global news, macro indicators' },
  { key: 'fundamentals', label: 'Fundamentals Analyst', desc: 'Financials, balance sheets' },
  { key: 'capital_flow', label: 'Capital Flow Analyst', desc: '主力资金流向, institutional flow' },
]

const DEPTH_OPTIONS = [
  { value: 1, label: 'Shallow', desc: '1 debate round' },
  { value: 3, label: 'Medium', desc: '3 debate rounds' },
  { value: 5, label: 'Deep', desc: '5 debate rounds' },
]

const AGENT_STAGES: Record<string, string> = {
  'Market Analyst': 'analysts', 'Sentiment Analyst': 'analysts',
  'News Analyst': 'analysts', 'Fundamentals Analyst': 'analysts',
  'Capital Flow Analyst': 'analysts',
  'Bull Researcher': 'research', 'Bear Researcher': 'research',
  'Research Manager': 'research',
  Trader: 'trader',
  'Aggressive Analyst': 'risk', 'Conservative Analyst': 'risk',
  'Neutral Analyst': 'risk',
  'Portfolio Manager': 'decision',
}

const AGENT_COLORS: Record<string, string> = {
  'Market Analyst': 'sky', 'Sentiment Analyst': 'violet',
  'News Analyst': 'emerald', 'Fundamentals Analyst': 'amber',
  'Capital Flow Analyst': 'orange',
  'Bull Researcher': 'green', 'Bear Researcher': 'red',
  'Research Manager': 'sky', Trader: 'cyan',
  'Aggressive Analyst': 'pink', 'Conservative Analyst': 'blue',
  'Neutral Analyst': 'slate',
  'Portfolio Manager': 'sky',
}

function reportSectionToAgentName(section: string): string {
  const map: Record<string, string> = {
    market_report: 'Market Analyst', sentiment_report: 'Sentiment Analyst',
    news_report: 'News Analyst', fundamentals_report: 'Fundamentals Analyst',
    capital_flow_report: 'Capital Flow Analyst',
    investment_plan: 'Research Manager',
    trader_investment_plan: 'Trader',
    final_trade_decision: 'Portfolio Manager',
  }
  return map[section] || section
}

export function RunAnalysis() {
  const navigate = useNavigate()
  const store = useAnalysisStore()
  const wsRef = useRef<WebSocket | null>(null)
  const elapsedRef = useRef(0)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Form state
  const [ticker, setTicker] = useState('SPY')
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10))
  const [analysts, setAnalysts] = useState(['market', 'social', 'news', 'fundamentals'])
  const [depth, setDepth] = useState(1)
  const [provider, setProvider] = useState('deepseek')
  const [quickModel, setQuickModel] = useState('deepseek-v4-flash')
  const [deepModel, setDeepModel] = useState('deepseek-v4-pro')
  const [language, setLanguage] = useState('English')
  const [providers, setProviders] = useState<ProviderInfo[]>([])
  const [modelOptions, setModelOptions] = useState<ModelOptions | null>(null)

  useEffect(() => {
    api.get<ProviderInfo[]>('/models/providers').then(setProviders).catch(() => {})
  }, [])

  useEffect(() => {
    api.get<ModelOptions>(`/models/${provider}`).then((data) => {
      setModelOptions(data)
      if (data.quick?.length > 0 && !data.quick.find((m) => m.value === quickModel)) {
        setQuickModel(data.quick[0].value)
      }
      if (data.deep?.length > 0 && !data.deep.find((m) => m.value === deepModel)) {
        setDeepModel(data.deep[0].value)
      }
    }).catch(() => {})
  }, [provider])

  const handleMessage = useCallback((msg: WSMessage) => {
    switch (msg.type) {
      case 'agent_status': {
        const p = msg.payload as { agent: string; status: string }
        store.updateAgentStatus(p.agent, p.status as AgentStatus)
        break
      }
      case 'report_chunk': {
        const p = msg.payload as { section: string; content: string }
        store.updateReportSection(p.section, p.content)
        const agent = reportSectionToAgentName(p.section)
        if (agent && !store.agentStatuses[agent]) {
          store.updateAgentStatus(agent, 'in_progress')
        }
        break
      }
      case 'stats': {
        const p = msg.payload as { llm_calls: number; tool_calls: number; tokens_in: number; tokens_out: number; elapsed_seconds: number }
        store.updateStats({ llm_calls: p.llm_calls, tool_calls: p.tool_calls, tokens_in: p.tokens_in, tokens_out: p.tokens_out, elapsed: p.elapsed_seconds })
        elapsedRef.current = p.elapsed_seconds
        break
      }
      case 'pipeline_stage': {
        const p = msg.payload as { stage: string }
        store.setPipelineStage(p.stage)
        break
      }
      case 'completion': {
        const p = msg.payload as { final_decision: string; rating: string; ticker: string; date: string }
        store.setCompleted(p)
        if (timerRef.current) clearInterval(timerRef.current)
        break
      }
      case 'error': {
        const p = msg.payload as { message: string; agent?: string }
        store.setError(p.message)
        if (timerRef.current) clearInterval(timerRef.current)
        break
      }
    }
  }, [store])

  const startAnalysis = async () => {
    const params: AnalysisParams = {
      ticker, date, analysts, research_depth: depth,
      llm_provider: provider, quick_think_llm: quickModel, deep_think_llm: deepModel,
      output_language: language, backend_url: null,
    }

    const result = await api.post<AnalysisRunResponse>('/analysis/run', params)
    store.startRun(result.run_id, ticker, date)

    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const ws = new WebSocket(`${protocol}://${window.location.host}/api/analysis/ws/${result.run_id}`)
    wsRef.current = ws

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data) as WSMessage
      handleMessage(msg)
    }
    ws.onerror = () => store.setError('WebSocket connection error')
    ws.onclose = () => { if (store.status === 'running') store.setError('Connection closed unexpectedly') }
  }

  const stopAnalysis = () => {
    if (wsRef.current) {
      wsRef.current.send('stop')
      wsRef.current.close()
    }
    if (store.runId) {
      api.post(`/analysis/stop/${store.runId}`)
    }
    if (timerRef.current) clearInterval(timerRef.current)
    store.reset()
  }

  const isRunning = store.status === 'running'
  const isDone = store.status === 'completed'
  const isError = store.status === 'error'

  useEffect(() => {
    if (isDone && store.completion) {
      const timer = setTimeout(() => {
        navigate(`/results/${store.completion!.ticker}/${store.completion!.date}`)
      }, 1500)
      return () => clearTimeout(timer)
    }
  }, [isDone, store.completion, navigate])

  // Build agent cards for grid
  const buildAgentCards = () => {
    const result: {
      key: string; name: string; status: AgentStatus;
      content: string | null; color: string;
      stage: 'analysts' | 'research' | 'trader' | 'risk' | 'decision'
    }[] = []

    const expectedAgents: { key: string; name: string; stage: string }[] = []
    if (analysts.includes('market')) expectedAgents.push({ key: 'market', name: 'Market Analyst', stage: 'analysts' })
    if (analysts.includes('social')) expectedAgents.push({ key: 'sentiment', name: 'Sentiment Analyst', stage: 'analysts' })
    if (analysts.includes('news')) expectedAgents.push({ key: 'news', name: 'News Analyst', stage: 'analysts' })
    if (analysts.includes('fundamentals')) expectedAgents.push({ key: 'fundamentals', name: 'Fundamentals Analyst', stage: 'analysts' })
    if (analysts.includes('capital_flow')) expectedAgents.push({ key: 'capital_flow', name: 'Capital Flow Analyst', stage: 'analysts' })
    expectedAgents.push(
      { key: 'bull', name: 'Bull Researcher', stage: 'research' },
      { key: 'bear', name: 'Bear Researcher', stage: 'research' },
      { key: 'rm', name: 'Research Manager', stage: 'research' },
      { key: 'trader', name: 'Trader', stage: 'trader' },
      { key: 'agg', name: 'Aggressive Analyst', stage: 'risk' },
      { key: 'con', name: 'Conservative Analyst', stage: 'risk' },
      { key: 'neu', name: 'Neutral Analyst', stage: 'risk' },
      { key: 'pm', name: 'Portfolio Manager', stage: 'decision' },
    )

    const reportToAgent: Record<string, string> = {
      market_report: 'Market Analyst', sentiment_report: 'Sentiment Analyst',
      news_report: 'News Analyst', fundamentals_report: 'Fundamentals Analyst',
      capital_flow_report: 'Capital Flow Analyst',
      investment_plan: 'Research Manager',
      trader_investment_plan: 'Trader',
      final_trade_decision: 'Portfolio Manager',
    }

    expectedAgents.forEach(({ key, name, stage }) => {
      const status = store.agentStatuses[name] || 'pending'
      let content: string | null = null
      for (const [section, agentName] of Object.entries(reportToAgent)) {
        if (agentName === name && store.reportSections[section]) {
          content = store.reportSections[section]
          break
        }
      }
      result.push({
        key, name, status: status as AgentStatus,
        content, color: AGENT_COLORS[name] || 'slate',
        stage: stage as 'analysts' | 'research' | 'trader' | 'risk' | 'decision',
      })
    })

    return result
  }

  return (
    <div className="max-w-6xl space-y-6">
      {/* Phase A: Configuration */}
      {!isRunning && !isDone && (
        <div className="grid grid-cols-2 gap-6">
          {/* Form */}
          <div className="space-y-5 bg-slate-900 border border-slate-800 rounded-xl p-5">
            <h3 className="font-semibold text-lg">Configuration</h3>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium block mb-1">Ticker</label>
                <input value={ticker} onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  className="w-full px-3 py-2 border border-slate-700 rounded-md text-sm bg-slate-950 focus:border-sky-500 focus:outline-none" />
              </div>
              <div>
                <label className="text-sm font-medium block mb-1">Date</label>
                <input type="date" value={date} onChange={(e) => setDate(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-700 rounded-md text-sm bg-slate-950 focus:border-sky-500 focus:outline-none" />
              </div>
            </div>

            <div>
              <label className="text-sm font-medium block mb-2">Analysts</label>
              <div className="grid grid-cols-2 gap-2">
                {ANALYST_OPTIONS.map((a) => (
                  <label key={a.key} className={`flex items-start gap-2 p-2.5 border rounded-md cursor-pointer transition-colors ${analysts.includes(a.key) ? 'border-sky-500/50 bg-sky-500/5' : 'border-slate-700 hover:border-slate-600'}`}>
                    <input type="checkbox" checked={analysts.includes(a.key)}
                      onChange={(e) => {
                        if (e.target.checked) setAnalysts([...analysts, a.key])
                        else setAnalysts(analysts.filter((k) => k !== a.key))
                      }} className="mt-0.5 accent-sky-500" />
                    <div>
                      <span className="text-sm font-medium">{a.label}</span>
                      <p className="text-xs text-slate-400">{a.desc}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="text-sm font-medium block mb-2">LLM Provider</label>
              <select value={provider} onChange={(e) => setProvider(e.target.value)}
                className="w-full px-3 py-2 border border-slate-700 rounded-md text-sm bg-slate-950 focus:border-sky-500 focus:outline-none">
                {providers.map((p) => <option key={p.key} value={p.key}>{p.display_name}</option>)}
              </select>
            </div>

            {modelOptions && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium block mb-1">Quick Model</label>
                  <select value={quickModel} onChange={(e) => setQuickModel(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-700 rounded-md text-sm bg-slate-950 focus:border-sky-500 focus:outline-none">
                    {modelOptions.quick.map((m) => <option key={m.value} value={m.value}>{m.label}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Deep Model</label>
                  <select value={deepModel} onChange={(e) => setDeepModel(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-700 rounded-md text-sm bg-slate-950 focus:border-sky-500 focus:outline-none">
                    {modelOptions.deep.map((m) => <option key={m.value} value={m.value}>{m.label}</option>)}
                  </select>
                </div>
              </div>
            )}

            <div>
              <label className="text-sm font-medium block mb-2">Research Depth</label>
              <div className="flex gap-3">
                {DEPTH_OPTIONS.map((d) => (
                  <button key={d.value} onClick={() => setDepth(d.value)}
                    className={`flex-1 p-3 border rounded-lg text-center transition-colors ${depth === d.value ? 'border-sky-500/50 bg-sky-500/5 ring-1 ring-sky-500/30' : 'border-slate-700 hover:border-slate-600'}`}>
                    <div className="font-semibold text-sm">{d.label}</div>
                    <div className="text-xs text-slate-400">{d.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-sm font-medium block mb-1">Output Language</label>
              <select value={language} onChange={(e) => setLanguage(e.target.value)}
                className="w-full px-3 py-2 border border-slate-700 rounded-md text-sm bg-slate-950 focus:border-sky-500 focus:outline-none">
                {['English', 'Chinese', 'Japanese', 'Korean', 'Spanish', 'Portuguese', 'French', 'German', 'Arabic', 'Russian', 'Hindi'].map((l) => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </select>
            </div>

            <button onClick={startAnalysis} disabled={analysts.length === 0}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-sky-500 text-slate-900 rounded-lg hover:bg-sky-400 transition-colors font-medium text-sm disabled:opacity-50">
              <Play className="w-4 h-4" /> Start Analysis
            </button>
          </div>

          {/* Preview */}
          <ConfigPreview
            ticker={ticker} date={date} analysts={analysts}
            provider={provider} quickModel={quickModel} deepModel={deepModel}
            depth={depth}
          />
        </div>
      )}

      {/* Phase B: Streaming */}
      {isRunning && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <PipelineProgress currentStage={(store.pipelineStage || 'analysts') as any} />
            <span className="text-sm text-slate-400 font-mono">
              {ticker} · {date}
            </span>
          </div>

          <AgentCardGrid agents={buildAgentCards()} />

          <StatsBar
            llmCalls={store.stats.llm_calls}
            toolCalls={store.stats.tool_calls}
            tokensIn={store.stats.tokens_in}
            tokensOut={store.stats.tokens_out}
            elapsed={store.stats.elapsed}
            onStop={stopAnalysis}
          />
        </div>
      )}

      {/* Phase C: Completion */}
      {isDone && store.completion && (
        <div className="bg-slate-900 border border-green-500/30 rounded-xl p-12 text-center space-y-4 shadow-[0_0_20px_rgba(34,197,94,0.1)]">
          <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto" />
          <h2 className="text-2xl font-bold">Analysis Complete</h2>
          <div className="flex justify-center">
            <RatingBadge rating={store.completion.rating} size="lg" />
          </div>
          <p className="text-slate-400">Redirecting to full results...</p>
        </div>
      )}

      {/* Phase D: Error */}
      {isError && (
        <div className="bg-slate-900 border border-red-500/30 rounded-xl p-12 text-center space-y-4">
          <XCircle className="w-16 h-16 text-red-500 mx-auto" />
          <h2 className="text-xl font-bold text-red-400">Analysis Failed</h2>
          <p className="text-slate-400 max-w-md mx-auto">{store.error}</p>
          <button onClick={() => store.reset()} className="px-6 py-2 bg-sky-500 text-slate-900 rounded-lg hover:bg-sky-400 transition-colors font-medium">
            Try Again
          </button>
        </div>
      )}
    </div>
  )
}
