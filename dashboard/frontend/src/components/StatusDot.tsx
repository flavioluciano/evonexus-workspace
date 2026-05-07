interface StatusDotProps {
  status: 'ok' | 'error' | 'pending'
}

export default function StatusDot({ status }: StatusDotProps) {
  const color = {
    ok: 'bg-[#00FFA7]',
    error: 'bg-red-400',
    pending: 'bg-yellow-400',
  }[status]

  return (
    <span className={`inline-block w-2.5 h-2.5 rounded-full ${color}`} />
  )
}
