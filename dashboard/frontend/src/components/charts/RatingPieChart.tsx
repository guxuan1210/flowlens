import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'

interface RatingCount {
  name: string
  value: number
  color: string
}

interface RatingPieChartProps {
  data: { rating?: string }[]
}

const RATING_COLORS: Record<string, string> = {
  Buy: 'hsl(142 76% 45%)',
  Overweight: 'hsl(82 76% 45%)',
  Hold: 'hsl(48 96% 53%)',
  Underweight: 'hsl(27 96% 55%)',
  Sell: 'hsl(0 84% 60%)',
}

export function RatingPieChart({ data }: RatingPieChartProps) {
  const counts: Record<string, number> = {}
  data.forEach((d) => {
    const r = d.rating || 'Unknown'
    counts[r] = (counts[r] || 0) + 1
  })

  const chartData: RatingCount[] = Object.entries(counts).map(([name, value]) => ({
    name,
    value,
    color: RATING_COLORS[name] || 'hsl(215 20% 65%)',
  }))

  if (chartData.length === 0) {
    return <div className="text-center py-8 text-slate-500 text-sm">No decisions recorded yet.</div>
  }

  return (
    <ResponsiveContainer width="100%" height={250}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius={50}
          outerRadius={90}
          paddingAngle={3}
          dataKey="value"
          stroke="hsl(222 47% 6%)"
          strokeWidth={2}
        >
          {chartData.map((entry, idx) => (
            <Cell key={idx} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            background: 'hsl(222 47% 9%)',
            border: '1px solid hsl(217 33% 18%)',
            borderRadius: '8px',
            fontSize: '12px',
          }}
          labelStyle={{ color: 'hsl(210 40% 98%)' }}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}
