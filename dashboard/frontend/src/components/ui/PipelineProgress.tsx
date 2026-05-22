import { cn } from '@/lib/utils'
import { CheckCircle2, Loader2 } from 'lucide-react'

type PipelineStage = 'analysts' | 'research' | 'trader' | 'risk' | 'decision'

const STAGES: { key: PipelineStage; label: string }[] = [
  { key: 'analysts', label: 'Analysts' },
  { key: 'research', label: 'Research' },
  { key: 'trader', label: 'Trader' },
  { key: 'risk', label: 'Risk' },
  { key: 'decision', label: 'Decision' },
]

interface PipelineProgressProps {
  currentStage: PipelineStage | null
}

export function PipelineProgress({ currentStage }: PipelineProgressProps) {
  const currentIdx = currentStage ? STAGES.findIndex((s) => s.key === currentStage) : -1

  return (
    <div className="flex items-center gap-1 bg-slate-900/50 border border-slate-800 rounded-lg px-4 py-2">
      {STAGES.map((stage, idx) => {
        const isCompleted = currentIdx > idx
        const isActive = currentIdx === idx
        const isPending = currentIdx < idx || currentIdx === -1

        return (
          <div key={stage.key} className="flex items-center gap-1">
            <div
              className={cn(
                'flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium transition-colors',
                isCompleted && 'text-green-400',
                isActive && 'text-sky-400 bg-sky-500/10',
                isPending && 'text-slate-600'
              )}
            >
              {isCompleted ? (
                <CheckCircle2 className="w-3.5 h-3.5" />
              ) : isActive ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <span className="w-3.5 h-3.5 rounded-full border border-slate-600" />
              )}
              <span>{stage.label}</span>
            </div>
            {idx < STAGES.length - 1 && (
              <span className="text-slate-700 text-xs">→</span>
            )}
          </div>
        )
      })}
    </div>
  )
}
