import { useState } from 'react'
import { api } from '@/api/client'
import { useAnalysisStore } from '@/store/analysisStore'
import type { HumanReviewPayload } from '@/types/streaming'
import { MarkdownReport } from '@/components/ui/MarkdownReport'
import { UserCheck, MessageSquareText, Loader2 } from 'lucide-react'

const RATING_OPTIONS = ['', 'Buy', 'Overweight', 'Hold', 'Underweight', 'Sell']

function getReviewTitle(reviewPoint: string): string {
  return reviewPoint === 'research_manager'
    ? 'Research Manager — Investment Plan Review'
    : 'Portfolio Manager — Final Decision Review'
}

function getMainContent(payload: HumanReviewPayload): string {
  if (payload.review_point === 'research_manager') {
    const plan = (payload.data.investment_plan as string) || ''
    const debate = (payload.data.debate_history as string) || ''
    let md = plan
    if (debate) {
      md += '\n\n---\n### Bull/Bear Debate Summary\n' + debate
    }
    return md
  }
  // portfolio_manager
  const decision = (payload.data.final_decision as string) || ''
  const traderPlan = (payload.data.trader_plan as string) || ''
  const pastContext = (payload.data.past_context as string) || ''
  let md = decision
  if (traderPlan) {
    md += '\n\n---\n### Trader Proposal\n' + traderPlan
  }
  if (pastContext) {
    md += '\n\n---\n### Past Context (from memory)\n' + pastContext
  }
  return md
}

export function HumanReviewPanel() {
  const store = useAnalysisStore()
  const [feedback, setFeedback] = useState('')
  const [ratingOverride, setRatingOverride] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const payload = store.humanReview
  if (!payload) return null

  const handleSubmit = async (action: 'approve' | 'revise') => {
    if (!store.runId) return
    setSubmitting(true)
    try {
      await api.post(`/analysis/${store.runId}/review`, {
        action,
        feedback: action === 'revise' ? feedback : '',
        rating_override: ratingOverride || null,
      })
      store.clearHumanReview()
    } catch (err) {
      console.error('Failed to submit review:', err)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="bg-slate-900 border border-amber-500/40 rounded-xl overflow-hidden shadow-[0_0_30px_rgba(245,158,11,0.1)]">
      {/* Header */}
      <div className="bg-amber-500/10 border-b border-amber-500/20 px-5 py-3 flex items-center gap-3">
        <div className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
        <h3 className="font-semibold text-amber-300 text-sm">
          Human Review Required — {getReviewTitle(payload.review_point)}
        </h3>
        <span className="text-xs text-amber-400/60 ml-auto font-mono">{payload.ticker}</span>
      </div>

      <div className="grid grid-cols-2 divide-x divide-slate-800">
        {/* Left: AI Decision */}
        <div className="p-4 max-h-[60vh] overflow-y-auto">
          <p className="text-xs text-slate-500 mb-2 uppercase tracking-wide">AI Decision / Proposal</p>
          <div className="prose prose-invert prose-sm max-w-none">
            <MarkdownReport content={getMainContent(payload)} />
          </div>
        </div>

        {/* Right: Human Input */}
        <div className="p-4 space-y-4">
          <div>
            <p className="text-xs text-slate-500 mb-2 uppercase tracking-wide">Your Feedback</p>
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Provide your feedback, concerns, or additional context for the AI to consider..."
              rows={8}
              className="w-full px-3 py-2 border border-slate-700 rounded-md text-sm bg-slate-950 focus:border-amber-500 focus:outline-none resize-none placeholder:text-slate-600"
            />
          </div>

          <div>
            <label className="text-xs text-slate-500 mb-1 block uppercase tracking-wide">
              Rating Override (optional)
            </label>
            <select
              value={ratingOverride}
              onChange={(e) => setRatingOverride(e.target.value)}
              className="w-full px-3 py-2 border border-slate-700 rounded-md text-sm bg-slate-950 focus:border-amber-500 focus:outline-none"
            >
              <option value="">Keep AI's rating</option>
              {RATING_OPTIONS.filter(Boolean).map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              onClick={() => handleSubmit('approve')}
              disabled={submitting}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-500 transition-colors font-medium text-sm disabled:opacity-50"
            >
              {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <UserCheck className="w-4 h-4" />}
              Approve
            </button>
            <button
              onClick={() => handleSubmit('revise')}
              disabled={submitting || !feedback.trim()}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-amber-600 text-white rounded-lg hover:bg-amber-500 transition-colors font-medium text-sm disabled:opacity-50"
            >
              {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <MessageSquareText className="w-4 h-4" />}
              Revise with Feedback
            </button>
          </div>
          {(payload.review_point === 'research_manager') && (
            <p className="text-xs text-slate-500">
              After review, the pipeline continues: Trader → Risk Analysts → Portfolio Manager.
            </p>
          )}
          {(payload.review_point === 'portfolio_manager') && (
            <p className="text-xs text-slate-500">
              This is the final decision gate. After review: Manipulation Risk Analysis → Complete.
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
