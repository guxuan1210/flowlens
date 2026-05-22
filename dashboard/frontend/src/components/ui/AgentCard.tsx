import { useState } from 'react'
import { cn } from '@/lib/utils'
import { CheckCircle2, Loader2, Clock, Wrench } from 'lucide-react'
import * as Dialog from '@radix-ui/react-dialog'
import { MarkdownReport } from './MarkdownReport'
import type { AgentStatus } from '@/types/streaming'

interface AgentCardProps {
  name: string
  status: AgentStatus
  content: string | null
  toolCalls?: number
  elapsed?: number
  color: string
}

export function AgentCard({ name, status, content, toolCalls = 0, elapsed, color }: AgentCardProps) {
  const [open, setOpen] = useState(false)

  const isRunning = status === 'in_progress'
  const isDone = status === 'completed'
  const isPending = status === 'pending'
  const isError = status === 'error'

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger asChild>
        <button
          className={cn(
            'relative text-left bg-slate-900 border rounded-xl p-4 transition-all duration-300 w-full',
            isDone && 'border-green-500/50 shadow-[0_0_12px_rgba(34,197,94,0.1)] hover:border-green-400',
            isRunning && 'border-sky-400/60 animate-[agent-pulse_2s_ease-in-out_infinite] hover:border-sky-300',
            isPending && 'border-dashed border-slate-700/60 opacity-50',
            isError && 'border-red-500/50'
          )}
          disabled={isPending}
        >
          {/* Header */}
          <div className="flex items-center gap-2 mb-2">
            <span
              className={cn('w-2 h-2 rounded-full shrink-0', {
                'bg-green-500': isDone,
                'bg-sky-400': isRunning,
                'bg-slate-600': isPending,
                'bg-red-500': isError,
              })}
            />
            <span
              className={cn('font-semibold text-sm truncate', {
                'text-green-400': isDone,
                'text-sky-400': isRunning,
                'text-slate-500': isPending,
                'text-red-400': isError,
              })}
            >
              {name}
            </span>
            {isRunning && (
              <Loader2 className="w-3.5 h-3.5 animate-spin text-sky-400 ml-auto shrink-0" />
            )}
            {isDone && (
              <CheckCircle2 className="w-3.5 h-3.5 text-green-500 ml-auto shrink-0" />
            )}
          </div>

          {/* Content preview */}
          <div className={cn('text-xs leading-relaxed line-clamp-3', isPending ? 'text-slate-600' : 'text-slate-300')}>
            {content || (isPending ? 'Waiting...' : 'No output yet')}
          </div>

          {/* Footer stats */}
          <div className="flex items-center gap-3 mt-3 text-[10px] text-slate-500">
            {elapsed !== undefined && (
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {elapsed}s
              </span>
            )}
            {toolCalls > 0 && (
              <span className="flex items-center gap-1">
                <Wrench className="w-3 h-3" />
                {toolCalls} tools
              </span>
            )}
          </div>

          {/* Expand CTA */}
          {isDone && content && (
            <div className="mt-2 text-[10px] text-sky-400/70">Click to expand →</div>
          )}
        </button>
      </Dialog.Trigger>

      {/* Full report dialog */}
      {isDone && content && (
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 bg-black/60 data-[state=open]:animate-in data-[state=closed]:animate-out" />
          <Dialog.Content className="fixed inset-x-4 top-[5%] bottom-[5%] max-w-4xl mx-auto bg-slate-900 border border-slate-700 rounded-xl shadow-2xl data-[state=open]:animate-in data-[state=closed]:animate-out overflow-hidden flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-slate-800 shrink-0">
              <Dialog.Title className="font-semibold text-lg">{name} Report</Dialog.Title>
              <Dialog.Close className="text-slate-400 hover:text-slate-200 transition-colors p-1 rounded-md hover:bg-slate-800">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </Dialog.Close>
            </div>
            <div className="flex-1 overflow-auto p-6">
              <MarkdownReport content={content} />
            </div>
          </Dialog.Content>
        </Dialog.Portal>
      )}
    </Dialog.Root>
  )
}
