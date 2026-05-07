import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface MetricCardProps {
  label: string
  value: string | number
  delta?: string
  deltaType?: 'up' | 'down' | 'neutral'
}

export default function MetricCard({ label, value, delta, deltaType = 'neutral' }: MetricCardProps) {
  const deltaColor = {
    up: 'text-[#00FFA7]',
    down: 'text-red-400',
    neutral: 'text-[#667085]',
  }[deltaType]

  const DeltaIcon = {
    up: TrendingUp,
    down: TrendingDown,
    neutral: Minus,
  }[deltaType]

  return (
    <div className="bg-[#182230] border border-[#344054] rounded-xl p-5 hover:border-[#00FFA7] transition-colors">
      <p className="text-sm text-[#667085] mb-1">{label}</p>
      <p className="text-2xl font-bold text-[#F9FAFB]">{value}</p>
      {delta && (
        <div className={`flex items-center gap-1 mt-2 text-xs ${deltaColor}`}>
          <DeltaIcon size={14} />
          <span>{delta}</span>
        </div>
      )}
    </div>
  )
}
