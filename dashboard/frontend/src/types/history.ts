export interface HistoryEntry {
  ticker: string
  date: string
  rating?: string
  raw_return?: string
  alpha_return?: string
  holding_days?: string
  pending: boolean
}

export interface HistoryListResponse {
  entries: HistoryEntry[]
  total: number
  limit: number
  offset: number
}

export interface TickerSummary {
  ticker: string
  total_analyses: number
  latest_date?: string
  latest_rating?: string
}
