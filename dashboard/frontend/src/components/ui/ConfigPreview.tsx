interface ConfigPreviewProps {
  ticker: string
  date: string
  analysts: string[]
  provider: string
  quickModel: string
  deepModel: string
  depth: number
}

const ANALYST_LABELS: Record<string, string> = {
  market: 'Market Analyst',
  social: 'Sentiment Analyst',
  news: 'News Analyst',
  fundamentals: 'Fundamentals Analyst',
}

const ANALYST_COLORS: Record<string, string> = {
  market: 'bg-sky-500/20 text-sky-400',
  social: 'bg-violet-500/20 text-violet-400',
  news: 'bg-emerald-500/20 text-emerald-400',
  fundamentals: 'bg-amber-500/20 text-amber-400',
}

export function ConfigPreview({ ticker, date, analysts, provider, quickModel, deepModel, depth }: ConfigPreviewProps) {
  return (
    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 space-y-4">
      <h3 className="font-semibold text-lg">Analysis Preview</h3>

      <div className="space-y-2 text-sm">
        <div className="flex items-center justify-between">
          <span className="text-slate-400">Ticker</span>
          <span className="font-mono font-bold text-sky-400">{ticker}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-slate-400">Date</span>
          <span className="text-slate-200">{date}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-slate-400">LLM</span>
          <span className="text-slate-200">{provider} / {deepModel} + {quickModel}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-slate-400">Depth</span>
          <span className="text-slate-200">{depth} debate round{depth > 1 ? 's' : ''}</span>
        </div>
      </div>

      <div>
        <span className="text-sm text-slate-400 block mb-2">Agents</span>
        <div className="flex flex-wrap gap-2">
          {analysts.map((a) => (
            <span key={a} className={`px-2 py-0.5 rounded-md text-xs font-medium ${ANALYST_COLORS[a] || 'bg-slate-500/20 text-slate-400'}`}>
              {ANALYST_LABELS[a] || a}
            </span>
          ))}
          <span className="px-2 py-0.5 rounded-md text-xs font-medium bg-slate-500/20 text-slate-400">+ Research + Trader + Risk + PM</span>
        </div>
      </div>

      <div className="pt-3 border-t border-slate-800">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span className="w-2 h-2 rounded-full bg-sky-400" />
          <span>Pipeline: Analysts → Research → Trader → Risk → Decision</span>
        </div>
      </div>
    </div>
  )
}
