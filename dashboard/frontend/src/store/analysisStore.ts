import { create } from 'zustand'
import type { AgentStatus, CompletionPayload } from '@/types/streaming'

interface AnalysisState {
  runId: string | null
  status: 'idle' | 'running' | 'completed' | 'error'
  ticker: string
  date: string
  agentStatuses: Record<string, AgentStatus>
  reportSections: Record<string, string>
  stats: { llm_calls: number; tool_calls: number; tokens_in: number; tokens_out: number; elapsed: number }
  completion: CompletionPayload | null
  error: string | null
  pipelineStage: string | null
  // Actions
  startRun: (runId: string, ticker: string, date: string) => void
  updateAgentStatus: (agent: string, status: AgentStatus) => void
  updateReportSection: (section: string, content: string) => void
  updateStats: (stats: { llm_calls: number; tool_calls: number; tokens_in: number; tokens_out: number; elapsed: number }) => void
  setCompleted: (payload: CompletionPayload) => void
  setError: (message: string) => void
  setPipelineStage: (stage: string) => void
  reset: () => void
}

const initialState = {
  runId: null as string | null,
  status: 'idle' as const,
  ticker: '',
  date: '',
  agentStatuses: {} as Record<string, AgentStatus>,
  reportSections: {} as Record<string, string>,
  stats: { llm_calls: 0, tool_calls: 0, tokens_in: 0, tokens_out: 0, elapsed: 0 },
  completion: null as CompletionPayload | null,
  error: null as string | null,
  pipelineStage: null as string | null,
}

export const useAnalysisStore = create<AnalysisState>((set) => ({
  ...initialState,
  startRun: (runId, ticker, date) =>
    set({ runId, ticker, date, status: 'running', agentStatuses: {}, reportSections: {}, stats: initialState.stats, completion: null, error: null, pipelineStage: null }),
  updateAgentStatus: (agent, status) =>
    set((s) => ({ agentStatuses: { ...s.agentStatuses, [agent]: status } })),
  updateReportSection: (section, content) =>
    set((s) => ({ reportSections: { ...s.reportSections, [section]: content } })),
  updateStats: (stats) => set({ stats }),
  setCompleted: (payload) => set({ status: 'completed', completion: payload }),
  setError: (message) => set({ status: 'error', error: message }),
  setPipelineStage: (stage: string) => set({ pipelineStage: stage }),
  reset: () => set(initialState),
}))
