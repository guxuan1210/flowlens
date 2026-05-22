import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface ReturnsDatum {
  ticker: string
  date: string
  raw_return?: number
  alpha_return?: number
  rating?: string
}

interface ReturnsChartProps {
  data: ReturnsDatum[]
}

export function ReturnsChart({ data }: ReturnsChartProps) {
  if (data.length === 0) {
    return <div className="text-center py-8 text-slate-500 text-sm">No performance data yet.</div>
  }

  const chartData = data
    .filter((d) => d.raw_return !== undefined)
    .slice(-10)
    .map((d) => ({
      name: `${d.ticker} ${d.date?.slice(5)}`,
      return: parseFloat((d.raw_return! * 100).toFixed(1)),
      alpha: d.alpha_return ? parseFloat((d.alpha_return * 100).toFixed(1)) : undefined,
    }))

  if (chartData.length === 0) {
    return <div className="text-center py-8 text-slate-500 text-sm">No resolved returns available yet.</div>
  }

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: -20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(217 33% 18%)" />
        <XAxis dataKey="name" tick={{ fontSize: 10, fill: 'hsl(215 20% 65%)' }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 10, fill: 'hsl(215 20% 65%)' }} axisLine={false} tickLine={false} unit="%" />
        <Tooltip
          contentStyle={{
            background: 'hsl(222 47% 9%)',
            border: '1px solid hsl(217 33% 18%)',
            borderRadius: '8px',
            fontSize: '12px',
          }}
          labelStyle={{ color: 'hsl(210 40% 98%)' }}
        />
        <Bar dataKey="return" radius={[4, 4, 0, 0]}>
          {chartData.map((entry, idx) => (
            <Cell
              key={idx}
              fill={entry.return >= 0 ? 'hsl(142 76% 45%)' : 'hsl(0 84% 60%)'}
              fillOpacity={0.8}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
