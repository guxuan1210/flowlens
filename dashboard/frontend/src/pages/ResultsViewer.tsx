import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '@/api/client'
import { MarkdownReport } from '@/components/ui/MarkdownReport'
import { RatingBadge } from '@/components/ui/RatingBadge'
import * as Tabs from '@radix-ui/react-tabs'
import { ArrowLeft } from 'lucide-react'

interface AnalysisState {
  company_of_interest: string
  trade_date: string
  market_report?: string
  sentiment_report?: string
  news_report?: string
  fundamentals_report?: string
  capital_flow_report?: string
  investment_debate_state?: {
    bull_history?: string
    bear_history?: string
    judge_decision?: string
  }
  trader_investment_plan?: string
  risk_debate_state?: {
    aggressive_history?: string
    conservative_history?: string
    neutral_history?: string
    judge_decision?: string
  }
  final_trade_decision?: string
}

const TABS = [
  { key: 'analysts', label: 'Analyst Reports' },
  { key: 'research', label: 'Research Debate' },
  { key: 'trader', label: 'Trading Plan' },
  { key: 'risk', label: 'Risk Analysis' },
  { key: 'decision', label: 'Final Decision' },
]

export function ResultsViewer() {
  const { ticker, date } = useParams<{ ticker: string; date: string }>()
  const [state, setState] = useState<AnalysisState | null>(null)
  const [activeTab, setActiveTab] = useState('analysts')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!ticker || !date) return
    api.get<AnalysisState>(`/history/${ticker}/${date}`)
      .then(setState)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [ticker, date])

  if (loading) return <div className="flex items-center justify-center h-64 text-slate-400">Loading...</div>
  if (!state) return <div className="flex items-center justify-center h-64 text-slate-400">Analysis not found.</div>

  const decision = state.final_trade_decision || state.risk_debate_state?.judge_decision || ''
  const ratingMatch = decision.match(/\*\*Rating\*\*:\s*(\w+)/)
  const rating = ratingMatch ? ratingMatch[1] : 'Hold'

  return (
    <div className="max-w-4xl space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/history" className="text-slate-400 hover:text-slate-200 transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold">{state.company_of_interest}</h1>
          <p className="text-slate-400 text-sm">{state.trade_date}</p>
        </div>
        <div className="ml-auto">
          <RatingBadge rating={rating} size="md" />
        </div>
      </div>

      <Tabs.Root value={activeTab} onValueChange={setActiveTab}>
        <Tabs.List className="flex gap-1 bg-slate-900 rounded-lg p-1 border border-slate-800">
          {TABS.map((t) => (
            <Tabs.Trigger
              key={t.key}
              value={t.key}
              className="flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors data-[state=active]:bg-slate-800 data-[state=active]:text-sky-400 data-[state=active]:shadow-sm text-slate-400 hover:text-slate-200"
            >
              {t.label}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <div className="mt-4 bg-slate-900 border border-slate-800 rounded-xl p-6">
          <Tabs.Content value="analysts" className="space-y-8">
            {state.market_report && <Section title="Market Analysis" content={state.market_report} />}
            {state.sentiment_report && <Section title="Sentiment Analysis" content={state.sentiment_report} />}
            {state.news_report && <Section title="News Analysis" content={state.news_report} />}
            {state.fundamentals_report && <Section title="Fundamentals Analysis" content={state.fundamentals_report} />}
            {state.capital_flow_report && <Section title="Capital Flow Analysis" content={state.capital_flow_report} />}
            {!state.market_report && !state.sentiment_report && !state.news_report && !state.fundamentals_report && !state.capital_flow_report && (
              <p className="text-slate-400 text-sm">No analyst reports available.</p>
            )}
          </Tabs.Content>

          <Tabs.Content value="research" className="space-y-8">
            {state.investment_debate_state?.bull_history && <Section title="Bull Researcher" content={state.investment_debate_state.bull_history} />}
            {state.investment_debate_state?.bear_history && <Section title="Bear Researcher" content={state.investment_debate_state.bear_history} />}
            {state.investment_debate_state?.judge_decision && <Section title="Research Manager Decision" content={state.investment_debate_state.judge_decision} />}
            {!state.investment_debate_state && <p className="text-slate-400 text-sm">No research debate recorded.</p>}
          </Tabs.Content>

          <Tabs.Content value="trader">
            <Section title="Trader Investment Plan" content={state.trader_investment_plan || 'No trader plan recorded.'} />
          </Tabs.Content>

          <Tabs.Content value="risk" className="space-y-8">
            {state.risk_debate_state?.aggressive_history && <Section title="Aggressive Analyst" content={state.risk_debate_state.aggressive_history} />}
            {state.risk_debate_state?.conservative_history && <Section title="Conservative Analyst" content={state.risk_debate_state.conservative_history} />}
            {state.risk_debate_state?.neutral_history && <Section title="Neutral Analyst" content={state.risk_debate_state.neutral_history} />}
            {!state.risk_debate_state && <p className="text-slate-400 text-sm">No risk analysis recorded.</p>}
          </Tabs.Content>

          <Tabs.Content value="decision">
            <Section title="Portfolio Manager Final Decision" content={decision || 'No final decision recorded.'} />
          </Tabs.Content>
        </div>
      </Tabs.Root>
    </div>
  )
}

function Section({ title, content }: { title: string; content: string }) {
  return (
    <div>
      <h3 className="font-semibold text-xs uppercase text-slate-500 tracking-wider mb-3">{title}</h3>
      <MarkdownReport content={content} />
    </div>
  )
}
