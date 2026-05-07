import { getAgentMeta } from '../lib/agent-meta'

interface AgentAvatarProps {
  name: string
  size?: number
  className?: string
}

export function AgentAvatar({ name, size = 48, className = '' }: AgentAvatarProps) {
  const meta = getAgentMeta(name)
  const Icon = meta.icon

  if (meta.avatar) {
    return (
      <img
        src={meta.avatar}
        alt={name}
        width={size}
        height={size}
        className={`rounded-full object-cover flex-shrink-0 ${className}`}
        style={{ width: size, height: size }}
      />
    )
  }

  // Fallback: Lucide icon inside a circle with the agent's color
  return (
    <div
      className={`rounded-full flex items-center justify-center flex-shrink-0 ${className}`}
      style={{
        width: size,
        height: size,
        backgroundColor: `${meta.color}20`,
        borderColor: meta.color,
        borderWidth: 1,
        borderStyle: 'solid',
      }}
    >
      <Icon size={Math.round(size * 0.5)} color={meta.color} />
    </div>
  )
}
