import { Routes, Route } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { Dashboard } from '@/pages/Dashboard'
import { RunAnalysis } from '@/pages/RunAnalysis'
import { ResultsViewer } from '@/pages/ResultsViewer'
import { History } from '@/pages/History'
import { Settings } from '@/pages/Settings'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/run" element={<RunAnalysis />} />
        <Route path="/results/:ticker/:date" element={<ResultsViewer />} />
        <Route path="/history" element={<History />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}
