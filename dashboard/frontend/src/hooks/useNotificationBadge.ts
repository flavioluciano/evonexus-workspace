import { useEffect, useRef } from 'react'

/**
 * Manages tab title badge and favicon badge based on pending approval count.
 *
 * - Tab title: prepends "(N) " when count > 0; prepends "🔔 " when hidden and needs attention.
 * - Favicon: draws a red dot on the existing favicon when count > 0.
 *
 * @param pendingCount  Total pending approvals across all sessions
 * @param needsAttention  True when a chat_complete fired while hidden (unread response)
 */
export function useNotificationBadge(pendingCount: number, needsAttention: boolean) {
  const originalTitleRef = useRef<string | null>(null)
  const originalFaviconRef = useRef<string | null>(null)
  const faviconLinkRef = useRef<HTMLLinkElement | null>(null)

  // Save original title on mount, restore on unmount
  useEffect(() => {
    originalTitleRef.current = document.title
    return () => {
      if (originalTitleRef.current !== null) {
        document.title = originalTitleRef.current
      }
    }
  }, [])

  // Update tab title when count/attention/visibility changes
  useEffect(() => {
    const base = originalTitleRef.current ?? document.title

    function updateTitle() {
      const hidden = document.hidden
      let prefix = ''
      if (pendingCount > 0) prefix = `(${pendingCount}) `
      if ((pendingCount > 0 || needsAttention) && hidden) prefix = '🔔 ' + prefix
      document.title = prefix + base
    }

    updateTitle()

    const onVisibility = () => updateTitle()
    document.addEventListener('visibilitychange', onVisibility)
    return () => {
      document.removeEventListener('visibilitychange', onVisibility)
    }
  }, [pendingCount, needsAttention])

  // Favicon badge
  useEffect(() => {
    // Find or cache the favicon link element
    if (!faviconLinkRef.current) {
      faviconLinkRef.current =
        (document.querySelector('link[rel="icon"]') as HTMLLinkElement | null) ||
        (document.querySelector('link[rel="shortcut icon"]') as HTMLLinkElement | null)
    }
    const link = faviconLinkRef.current
    if (!link) return

    if (pendingCount === 0) {
      // Restore original favicon
      if (originalFaviconRef.current) {
        link.href = originalFaviconRef.current
      }
      return
    }

    const drawBadge = (sourceUrl: string) => {
      try {
        const canvas = document.createElement('canvas')
        canvas.width = 32
        canvas.height = 32
        const ctx = canvas.getContext('2d')
        if (!ctx) return

        const img = new Image()
        // Allow cross-origin images (data URLs are fine)
        img.crossOrigin = 'anonymous'
        img.onload = () => {
          try {
            ctx.clearRect(0, 0, 32, 32)
            ctx.drawImage(img, 0, 0, 32, 32)

            // Red dot — top-right corner
            const dotR = 6
            const cx = 32 - dotR - 1
            const cy = dotR + 1
            ctx.beginPath()
            ctx.arc(cx, cy, dotR, 0, Math.PI * 2)
            ctx.fillStyle = '#ef4444'
            ctx.fill()

            const dataUrl = canvas.toDataURL('image/png')
            // Force favicon refresh: remove and re-add the link element
            const parent = link.parentNode
            if (parent) {
              parent.removeChild(link)
              link.href = dataUrl
              parent.appendChild(link)
            } else {
              link.href = dataUrl
            }
          } catch {
            // Canvas taint or other error — no-op
          }
        }
        img.onerror = () => {
          // Could not load favicon image — no-op
        }
        img.src = sourceUrl
      } catch {
        // No-op on any error
      }
    }

    if (!originalFaviconRef.current) {
      // First time: capture original href, then draw badge
      originalFaviconRef.current = link.href
    }

    drawBadge(originalFaviconRef.current)
  }, [pendingCount])
}
