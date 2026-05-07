import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bell, BellRing, CheckCircle2, X } from 'lucide-react'
import { useNotifications } from '../context/NotificationContext'
import type { GlobalNotification } from '../hooks/useGlobalNotifications'

function relativeTime(ts: number): string {
  const diff = Math.floor((Date.now() - ts) / 1000)
  if (diff < 5) return 'just now'
  if (diff < 60) return `${diff}s ago`
  const m = Math.floor(diff / 60)
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

function toolLabel(n: GlobalNotification): string {
  if (n.toolName) return n.toolName
  return 'tool'
}

function inputPreview(n: GlobalNotification): string {
  if (n.inputPreview) return n.inputPreview.slice(0, 60)
  return ''
}

export default function NotificationBell() {
  const { notifications, unreadCount, dismiss, dismissAll } = useNotifications()
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()
  const panelRef = useRef<HTMLDivElement>(null)
  const buttonRef = useRef<HTMLButtonElement>(null)

  // Close on outside click
  useEffect(() => {
    if (!open) return
    function onDown(e: MouseEvent) {
      if (
        panelRef.current && !panelRef.current.contains(e.target as Node) &&
        buttonRef.current && !buttonRef.current.contains(e.target as Node)
      ) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', onDown)
    return () => document.removeEventListener('mousedown', onDown)
  }, [open])

  function handleEntryClick(n: GlobalNotification) {
    dismiss(n.id)
    setOpen(false)
    navigate(`/agents/${encodeURIComponent(n.agentName)}`)
  }

  return (
    <div className="relative">
      <button
        ref={buttonRef}
        onClick={() => setOpen(v => !v)}
        className="relative p-1.5 rounded-lg text-[#667085] hover:text-[#D0D5DD] hover:bg-white/5 transition-colors"
        title="Notifications"
      >
        <Bell size={16} />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 min-w-[14px] h-[14px] px-0.5 rounded-full bg-[#00FFA7] text-[#0C111D] text-[9px] font-bold flex items-center justify-center leading-none">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div
          ref={panelRef}
          className="absolute left-full top-0 ml-2 w-[360px] max-h-[480px] flex flex-col rounded-xl border border-[#21262d] bg-[#161b22] shadow-2xl z-[100] overflow-hidden"
          style={{ minWidth: 280 }}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-[#21262d]">
            <span className="text-sm font-semibold text-[#D0D5DD]">Notifications</span>
            {notifications.length > 0 && (
              <button
                onClick={dismissAll}
                className="text-xs text-[#667085] hover:text-[#D0D5DD] transition-colors"
              >
                Clear all
              </button>
            )}
          </div>

          {/* List */}
          <div className="flex-1 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="px-4 py-8 text-center text-sm text-[#667085]">
                No notifications
              </div>
            ) : (
              [...notifications].reverse().map((n, idx) => (
                <div key={n.id}>
                  {idx > 0 && <div className="border-t border-[#21262d]/60" />}
                  <button
                    className="w-full text-left px-4 py-3 hover:bg-white/5 transition-colors flex items-start gap-3 group"
                    onClick={() => handleEntryClick(n)}
                  >
                    {/* Unread dot */}
                    <span className={`mt-1.5 w-1.5 h-1.5 rounded-full shrink-0 ${n.read ? 'bg-transparent' : 'bg-[#00FFA7]'}`} />

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5">
                        {n.event === 'agent_awaiting'
                          ? <BellRing size={12} className="text-[#00FFA7] shrink-0" />
                          : <CheckCircle2 size={12} className="text-[#667085] shrink-0" />}
                        <span className="text-sm font-semibold text-[#D0D5DD] truncate">
                          @{n.agentName}
                        </span>
                      </div>
                      <p className="text-xs text-[#667085] mt-0.5 truncate">
                        {n.event === 'agent_awaiting'
                          ? `${toolLabel(n)} — needs approval${inputPreview(n) ? `: ${inputPreview(n)}` : ''}`
                          : 'finished turn'}
                      </p>
                    </div>

                    <div className="flex flex-col items-end gap-1 shrink-0">
                      <span className="text-[10px] text-[#667085]">{relativeTime(n.createdAt)}</span>
                      <button
                        className="text-[#667085] opacity-0 group-hover:opacity-100 transition-opacity hover:text-[#D0D5DD]"
                        onClick={(e) => { e.stopPropagation(); dismiss(n.id) }}
                        aria-label="Dismiss"
                      >
                        <X size={12} />
                      </button>
                    </div>
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}
