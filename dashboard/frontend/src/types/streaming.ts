export type AgentStatus = 'pending' | 'in_progress' | 'completed' | 'error'

export interface AgentStatusPayload {
  agent: string
  status: AgentStatus
}

export interface ReportChunkPayload {
  section: string
  content: string
}

export interface StatsPayload {
  llm_calls: number
  tool_calls: number
  tokens_in: number
  tokens_out: number
  elapsed_seconds: number
}

export interface CompletionPayload {
  final_decision: string
  rating: string
  ticker: string
  date: string
}

export interface ErrorPayload {
  message: string
  agent?: string
}

export interface HumanReviewPayload {
  review_point: 'research_manager' | 'portfolio_manager'
  ticker: string
  data: Record<string, unknown>
}

export type WSMessageType =
  | 'agent_status'
  | 'report_chunk'
  | 'stats'
  | 'message'
  | 'tool_call'
  | 'completion'
  | 'error'
  | 'pipeline_stage'
  | 'human_review_required'

export interface WSMessage {
  type: WSMessageType
  timestamp: string
  payload: AgentStatusPayload | ReportChunkPayload | StatsPayload | CompletionPayload | ErrorPayload | HumanReviewPayload | Record<string, unknown>
}
