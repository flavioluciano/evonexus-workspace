import { createContext, useContext, type ReactNode } from 'react'
import { useGlobalNotifications, type GlobalNotification } from '../hooks/useGlobalNotifications'

interface NotificationContextValue {
  notifications: GlobalNotification[]
  unreadCount: number
  dismiss: (id: string) => void
  dismissBySession: (sessionId: string) => void
  dismissAll: () => void
}

const NotificationContext = createContext<NotificationContextValue | null>(null)

export function NotificationProvider({ children }: { children: ReactNode }) {
  const value = useGlobalNotifications()
  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  )
}

export function useNotifications(): NotificationContextValue {
  const ctx = useContext(NotificationContext)
  if (!ctx) throw new Error('useNotifications must be used inside <NotificationProvider>')
  return ctx
}
