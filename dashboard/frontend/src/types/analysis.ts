export interface AnalysisParams {
  ticker: string
  date: string
  analysts: string[]
  research_depth: number
  llm_provider: string
  quick_think_llm: string
  deep_think_llm: string
  backend_url?: string | null
  output_language: string
  google_thinking_level?: string | null
  openai_reasoning_effort?: string | null
  anthropic_effort?: string | null
  enable_human_review?: boolean
  human_review_points?: string[]
}

export interface AnalysisRunResponse {
  run_id: string
  ws_url: string
  status_url: string
}

export interface AnalysisStatusResponse {
  run_id: string
  status: string
  agent_statuses: Record<string, string>
  stats?: Record<string, unknown>
  report_sections: Record<string, string>
  final_decision?: string
  error?: string
}
