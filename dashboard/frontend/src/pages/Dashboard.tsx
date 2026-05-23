import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '@/api/client'
import { Play, BarChart3, TrendingUp, TrendingDown } from 'lucide-react'
import { ReturnsChart } from '@/components/charts/ReturnsChart'
import { RatingPieChart } from '@/components/charts/RatingPieChart'
import { EmptyState } from '@/components/ui/EmptyState'
import { RatingBadge } from '@/components/ui/RatingBadge'
import type { HistoryEntry } from '@/types/history'

export function Dashboard() {
  const [entries, setEntries] = useState<HistoryEntry[]>([])
  const [stats, setStats] = useState({ total: 0, buyCount: 0, sellCount: 0 })

  useEffect(() => {
    api.get<{ entries: HistoryEntry[]; total: number }>('/history?limit=100').then((data) => {
      setEntries(data.entries.filter((e) => !e.pending))
      setStats({ total: data.total, buyCount: 0, sellCount: 0 })
    }).catch(() => {})
    api.get<{ entries: HistoryEntry[]; total: number }>('/memory?limit=500').then((data) => {
      const resolved = data.entries.filter((e: HistoryEntry) => !e.pending)
      const buy = resolved.filter((e: HistoryEntry) => e.rating === 'Buy' || e.rating === 'Overweight').length
      const sell = resolved.filter((e: HistoryEntry) => e.rating === 'Sell' || e.rating === 'Underweight').length
      setStats({ total: resolved.length, buyCount: buy, sellCount: sell })
    }).catch(() => {})
  }, [])

  const cards = [
    { label: 'Total Analyses', value: stats.total, icon: BarChart3, color: 'text-sky-400' },
    { label: 'Buy Signals', value: stats.buyCount, icon: TrendingUp, color: 'text-green-400' },
    { label: 'Sell Signals', value: stats.sellCount, icon: TrendingDown, color: 'text-red-400' },
  ]

  const hasData = entries.length > 0 || stats.total > 0

  return (
    <div className="max-w-6xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">TradingAgents Dashboard</h1>
          <p className="text-slate-400 mt-1">Multi-Agent LLM Financial Trading Framework</p>
        </div>
        <Link
          to="/run"
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-sky-500 text-slate-900 rounded-lg hover:bg-sky-400 transition-colors font-medium text-sm"
        >
          <Play className="w-4 h-4" /> New Analysis
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-3 gap-4">
        {cards.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">{label}</span>
              <Icon className={`w-5 h-5 ${color}`} />
            </div>
            <p className="text-3xl font-bold mt-2">{value}</p>
          </div>
        ))}
      </div>

      {!hasData ? (
        <EmptyState
          title="No analyses yet"
          description="Run your first analysis to see performance charts and insights here."
          actionLabel="Run Analysis"
          actionTo="/run"
        />
      ) : (
        <>
          {/* Charts Row */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <h3 className="font-semibold text-sm mb-4">Return Distribution</h3>
              <ReturnsChart data={entries.map((e) => ({ ...e, raw_return: e.raw_return ? parseFloat(e.raw_return) : undefined }))} />
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <h3 className="font-semibold text-sm mb-4">Rating Distribution</h3>
              <RatingPieChart data={entries} />
            </div>
          </div>

          {/* Recent Analyses */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl">
            <div className="p-4 border-b border-slate-800">
              <h3 className="font-semibold text-sm">Recent Analyses</h3>
            </div>
            <div className="divide-y divide-slate-800">
              {entries.slice(0, 5).map((entry) => (
                <Link
                  key={`${entry.ticker}-${entry.date}`}
                  to={`/results/${entry.ticker}/${entry.date}`}
                  className="flex items-center justify-between px-4 py-3 hover:bg-slate-800/50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <span className="font-mono font-semibold text-sky-400">{entry.ticker}</span>
                    <span className="text-slate-400 text-sm">{entry.date}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    {entry.rating && <RatingBadge rating={entry.rating} size="sm" />}
                    {entry.raw_return && (
                      <span className={`font-mono text-sm ${entry.raw_return.startsWith('+') ? 'text-green-400' : entry.raw_return.startsWith('-') ? 'text-red-400' : 'text-slate-400'}`}>
                        {entry.raw_return}
                      </span>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
