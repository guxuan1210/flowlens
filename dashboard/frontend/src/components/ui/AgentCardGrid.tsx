import { AgentCard } from './AgentCard'
import type { AgentStatus } from '@/types/streaming'

interface CardAgent {
  key: string
  name: string
  status: AgentStatus
  content: string | null
  toolCalls?: number
  elapsed?: number
  color: string
  stage: 'analysts' | 'research' | 'trader' | 'risk' | 'decision'
}

interface AgentCardGridProps {
  agents: CardAgent[]
}

const STAGE_LABELS: Record<string, string> = {
  analysts: 'I. Analyst Team',
  research: 'II. Research Team',
  trader: 'III. Trader',
  risk: 'IV. Risk Management',
  decision: 'V. Portfolio Manager',
}

export function AgentCardGrid({ agents }: AgentCardGridProps) {
  const stages = ['analysts', 'research', 'trader', 'risk', 'decision'] as const

  return (
    <div className="space-y-6">
      {stages.map((stage) => {
        const stageAgents = agents.filter((a) => a.stage === stage)
        if (stageAgents.length === 0) return null

        return (
          <div key={stage}>
            <h3 className="text-xs font-semibold uppercase text-slate-500 tracking-wider mb-3">
              {STAGE_LABELS[stage]}
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
              {stageAgents.map((agent) => (
                <AgentCard
                  key={agent.key}
                  name={agent.name}
                  status={agent.status}
                  content={agent.content}
                  toolCalls={agent.toolCalls}
                  elapsed={agent.elapsed}
                  color={agent.color}
                />
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}
