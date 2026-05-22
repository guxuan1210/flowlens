import { Brain, Wrench, ArrowUp, ArrowDown, Clock } from 'lucide-react'

interface StatsBarProps {
  llmCalls: number
  toolCalls: number
  tokensIn: number
  tokensOut: number
  elapsed: number
  onStop?: () => void
}

function fmt(n: number): string {
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`
  return String(n)
}

export function StatsBar({ llmCalls, toolCalls, tokensIn, tokensOut, elapsed, onStop }: StatsBarProps) {
  const mins = Math.floor(elapsed / 60)
  const secs = Math.floor(elapsed % 60)

  return (
    <div className="flex items-center justify-between bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-400">
      <div className="flex items-center gap-6">
        <span className="flex items-center gap-1.5">
          <Brain className="w-4 h-4" />
          <span className="text-slate-200 font-mono">{llmCalls}</span>
          <span className="text-xs">LLM</span>
        </span>
        <span className="flex items-center gap-1.5">
          <Wrench className="w-4 h-4" />
          <span className="text-slate-200 font-mono">{toolCalls}</span>
          <span className="text-xs">Tools</span>
        </span>
        <span className="flex items-center gap-1.5">
          <ArrowUp className="w-3.5 h-3.5 text-green-400" />
          <span className="text-slate-200 font-mono">{fmt(tokensIn)}</span>
          <ArrowDown className="w-3.5 h-3.5 text-red-400" />
          <span className="text-slate-200 font-mono">{fmt(tokensOut)}</span>
          <span className="text-xs">Tokens</span>
        </span>
      </div>
      <div className="flex items-center gap-4">
        <span className="flex items-center gap-1.5">
          <Clock className="w-4 h-4" />
          <span className="text-slate-200 font-mono">{mins}:{secs.toString().padStart(2, '0')}</span>
        </span>
        {onStop && (
          <button
            onClick={onStop}
            className="px-3 py-1 bg-red-500/10 text-red-400 border border-red-500/30 rounded-md text-xs font-medium hover:bg-red-500/20 transition-colors"
          >
            Stop
          </button>
        )}
      </div>
    </div>
  )
}
