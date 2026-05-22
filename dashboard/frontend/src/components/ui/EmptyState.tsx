import { Link } from 'react-router-dom'
import { Play } from 'lucide-react'

interface EmptyStateProps {
  title: string
  description: string
  actionLabel?: string
  actionTo?: string
}

export function EmptyState({ title, description, actionLabel, actionTo }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mb-4">
        <Play className="w-6 h-6 text-slate-500" />
      </div>
      <h3 className="font-semibold text-lg mb-1">{title}</h3>
      <p className="text-slate-400 text-sm mb-4 max-w-sm">{description}</p>
      {actionLabel && actionTo && (
        <Link
          to={actionTo}
          className="inline-flex items-center gap-2 px-4 py-2 bg-sky-500 text-slate-900 rounded-lg hover:bg-sky-400 transition-colors font-medium text-sm"
        >
          <Play className="w-4 h-4" />
          {actionLabel}
        </Link>
      )}
    </div>
  )
}
