import { cn } from '@/lib/utils'

const RATING_STYLES: Record<string, string> = {
  Buy: 'bg-green-500/20 text-green-400 border-green-500/30',
  Overweight: 'bg-lime-500/20 text-lime-400 border-lime-500/30',
  Hold: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  Underweight: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  Sell: 'bg-red-500/20 text-red-400 border-red-500/30',
}

interface RatingBadgeProps {
  rating: string
  size?: 'sm' | 'md' | 'lg'
}

export function RatingBadge({ rating, size = 'md' }: RatingBadgeProps) {
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-6 py-2 text-2xl font-bold',
  }

  return (
    <span
      className={cn(
        'inline-block rounded-lg border font-semibold tracking-wide',
        sizeClasses[size],
        RATING_STYLES[rating] || 'bg-slate-500/20 text-slate-400 border-slate-500/30'
      )}
    >
      {rating || '--'}
    </span>
  )
}
