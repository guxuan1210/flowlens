import { useLocation } from 'react-router-dom'

const titles: Record<string, string> = {
  '/': 'Dashboard',
  '/run': 'Run Analysis',
  '/history': 'History',
  '/settings': 'Settings',
}

export function Header() {
  const location = useLocation()
  const title = titles[location.pathname]
    || (location.pathname.startsWith('/results') ? 'Analysis Results' : 'TradingAgents')

  return (
    <header className="h-14 border-b bg-card flex items-center px-6 shrink-0">
      <h2 className="text-lg font-semibold">{title}</h2>
    </header>
  )
}
