import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '@/api/client'
import { RatingBadge } from '@/components/ui/RatingBadge'
import { EmptyState } from '@/components/ui/EmptyState'
import { Search } from 'lucide-react'
import type { HistoryEntry } from '@/types/history'

export function History() {
  const [entries, setEntries] = useState<HistoryEntry[]>([])
  const [total, setTotal] = useState(0)
  const [tickerFilter, setTickerFilter] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    const params = new URLSearchParams({ limit: '100', offset: '0' })
    if (tickerFilter) params.set('ticker', tickerFilter.toUpperCase())
    api.get<{ entries: HistoryEntry[]; total: number }>(`/history?${params}`)
      .then((data) => { setEntries(data.entries); setTotal(data.total) })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [tickerFilter])

  return (
    <div className="max-w-5xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Analysis History</h1>
        <p className="text-slate-400 mt-1">{total} analyses recorded</p>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
        <input
          value={tickerFilter}
          onChange={(e) => setTickerFilter(e.target.value)}
          placeholder="Filter by ticker..."
          className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm focus:border-sky-500 focus:outline-none"
        />
      </div>

      {loading ? (
        <div className="text-center py-8 text-slate-400">Loading...</div>
      ) : entries.length === 0 ? (
        <EmptyState
          title={tickerFilter ? `No analyses for ${tickerFilter}` : 'No analyses yet'}
          description={tickerFilter ? 'Try a different ticker filter.' : 'Run your first analysis to see it here.'}
          actionLabel={tickerFilter ? undefined : 'Run Analysis'}
          actionTo={tickerFilter ? undefined : '/run'}
        />
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="grid grid-cols-[2fr_1fr_1fr_1fr_1fr] gap-4 p-3 border-b border-slate-800 bg-slate-900/50 text-xs font-semibold uppercase text-slate-500">
            <span>Ticker</span>
            <span>Date</span>
            <span>Rating</span>
            <span>Return</span>
            <span>Alpha</span>
          </div>
          <div className="divide-y divide-slate-800">
            {entries.map((entry) => (
              <Link
                key={`${entry.ticker}-${entry.date}`}
                to={`/results/${entry.ticker}/${entry.date}`}
                className="grid grid-cols-[2fr_1fr_1fr_1fr_1fr] gap-4 p-3 hover:bg-slate-800/50 transition-colors text-sm items-center"
              >
                <span className="font-mono font-semibold text-sky-400">{entry.ticker}</span>
                <span className="text-slate-400">{entry.date}</span>
                <span>
                  {entry.rating ? (
                    <RatingBadge rating={entry.rating} size="sm" />
                  ) : entry.pending ? (
                    <span className="text-xs text-amber-400">Pending</span>
                  ) : (
                    <span className="text-xs text-slate-500">--</span>
                  )}
                </span>
                <span className={`font-mono ${entry.raw_return?.startsWith('+') ? 'text-green-400' : entry.raw_return?.startsWith('-') ? 'text-red-400' : 'text-slate-400'}`}>
                  {entry.raw_return || '--'}
                </span>
                <span className={`font-mono ${entry.alpha_return?.startsWith('+') ? 'text-green-400' : entry.alpha_return?.startsWith('-') ? 'text-red-400' : 'text-slate-400'}`}>
                  {entry.alpha_return || '--'}
                </span>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
