import { useState, useEffect, useCallback } from 'react'
import { Share2, Copy, Check, Trash2, RefreshCw, Link } from 'lucide-react'
import { api } from '../lib/api'

interface ShareRecord {
  id: number
  token: string
  path: string
  created_by: string | null
  created_at: string | null
  expires_at: string | null
  view_count: number
  enabled: boolean
}

function formatDate(iso: string | null): string {
  if (!iso) return '—'
  try {
    return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(iso))
  } catch {
    return iso
  }
}

function statusLabel(share: ShareRecord): { label: string; color: string } {
  if (!share.enabled) return { label: 'Revogado', color: '#f87171' }
  if (share.expires_at) {
    const now = new Date()
    const exp = new Date(share.expires_at)
    if (now > exp) return { label: 'Expirado', color: '#fbbf24' }
  }
  return { label: 'Ativo', color: '#00FFA7' }
}

export default function ShareLinks() {
  const [shares, setShares] = useState<ShareRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [copiedToken, setCopiedToken] = useState<string | null>(null)
  const [confirmRevoke, setConfirmRevoke] = useState<ShareRecord | null>(null)
  const [revoking, setRevoking] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.get('/shares')
      setShares(data.shares || [])
    } catch {
      setError('Erro ao carregar links de compartilhamento.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const handleCopy = (token: string) => {
    const base = `${window.location.protocol}//${window.location.host}`
    const url = `${base}/share/${token}`
    navigator.clipboard.writeText(url).then(() => {
      setCopiedToken(token)
      setTimeout(() => setCopiedToken(null), 2000)
    })
  }

  const handleRevoke = async (share: ShareRecord) => {
    setRevoking(share.token)
    try {
      await api.delete(`/shares/${share.token}`)
      setShares(prev => prev.map(s => s.token === share.token ? { ...s, enabled: false } : s))
    } catch {
      // silently fail — reload will show real state
    } finally {
      setRevoking(null)
      setConfirmRevoke(null)
    }
  }

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              background: 'rgba(0,255,167,0.1)',
              border: '1px solid rgba(0,255,167,0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Share2 size={18} style={{ color: 'var(--evo-green)' }} />
          </div>
          <div>
            <h1 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
              Links de Compartilhamento
            </h1>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
              Gerencie os links públicos de arquivos do workspace
            </p>
          </div>
        </div>
        <button
          onClick={load}
          className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm transition-colors"
          style={{ color: 'var(--text-secondary)', border: '1px solid var(--border)' }}
          onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--surface-hover)' }}
          onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent' }}
        >
          <RefreshCw size={13} />
          Atualizar
        </button>
      </div>

      {/* Content */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <span style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Carregando...</span>
        </div>
      )}

      {!loading && error && (
        <div
          className="p-4 rounded-xl text-sm"
          style={{ background: 'rgba(239,68,68,0.1)', color: '#f87171', border: '1px solid rgba(239,68,68,0.3)' }}
        >
          {error}
        </div>
      )}

      {!loading && !error && shares.length === 0 && (
        <div
          className="flex flex-col items-center justify-center py-20 rounded-xl"
          style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}
        >
          <Link size={32} style={{ color: 'var(--text-muted)', marginBottom: '12px' }} />
          <p style={{ color: 'var(--text-primary)', fontSize: '15px', fontWeight: 600, marginBottom: '6px' }}>
            Nenhum link de compartilhamento
          </p>
          <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
            Crie um link ao compartilhar um arquivo no Workspace.
          </p>
        </div>
      )}

      {!loading && !error && shares.length > 0 && (
        <div
          className="rounded-xl overflow-hidden"
          style={{ border: '1px solid var(--border)', background: 'var(--bg-card)' }}
        >
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                {['Arquivo', 'Criado por', 'Criado em', 'Expira em', 'Visualizações', 'Status', 'Ações'].map((col) => (
                  <th
                    key={col}
                    style={{
                      padding: '10px 16px',
                      textAlign: 'left',
                      fontSize: '11px',
                      fontWeight: 600,
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                      color: 'var(--text-muted)',
                    }}
                  >
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {shares.map((share, i) => {
                const status = statusLabel(share)
                const isActive = share.enabled && (!share.expires_at || new Date() < new Date(share.expires_at))
                return (
                  <tr
                    key={share.id}
                    style={{
                      borderBottom: i < shares.length - 1 ? '1px solid var(--border)' : 'none',
                      background: 'transparent',
                      transition: 'background 100ms',
                    }}
                    onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = 'var(--surface-hover)' }}
                    onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = 'transparent' }}
                  >
                    {/* File path */}
                    <td style={{ padding: '10px 16px' }}>
                      <span
                        className="font-mono text-xs"
                        style={{ color: 'var(--text-primary)', wordBreak: 'break-all' }}
                        title={share.path}
                      >
                        {share.path.split('/').pop() ?? share.path}
                      </span>
                      <br />
                      <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                        {share.path}
                      </span>
                    </td>

                    {/* Created by */}
                    <td style={{ padding: '10px 16px' }}>
                      <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                        {share.created_by ?? '—'}
                      </span>
                    </td>

                    {/* Created at */}
                    <td style={{ padding: '10px 16px', whiteSpace: 'nowrap' }}>
                      <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                        {formatDate(share.created_at)}
                      </span>
                    </td>

                    {/* Expires at */}
                    <td style={{ padding: '10px 16px', whiteSpace: 'nowrap' }}>
                      <span className="text-xs" style={{ color: share.expires_at ? 'var(--text-secondary)' : 'var(--text-muted)' }}>
                        {share.expires_at ? formatDate(share.expires_at) : 'Sem expiração'}
                      </span>
                    </td>

                    {/* View count */}
                    <td style={{ padding: '10px 16px', textAlign: 'center' }}>
                      <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                        {share.view_count}
                      </span>
                    </td>

                    {/* Status */}
                    <td style={{ padding: '10px 16px' }}>
                      <span
                        className="text-xs px-2 py-0.5 rounded-full font-medium"
                        style={{
                          background: `${status.color}15`,
                          color: status.color,
                          border: `1px solid ${status.color}33`,
                        }}
                      >
                        {status.label}
                      </span>
                    </td>

                    {/* Actions */}
                    <td style={{ padding: '10px 16px' }}>
                      <div className="flex items-center gap-1.5">
                        {/* Copy link */}
                        <button
                          onClick={() => handleCopy(share.token)}
                          className="p-1.5 rounded-lg transition-colors"
                          style={{
                            color: copiedToken === share.token ? 'var(--evo-green)' : 'var(--text-muted)',
                            background: 'transparent',
                          }}
                          title="Copiar link"
                          onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--surface-hover)' }}
                          onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent' }}
                        >
                          {copiedToken === share.token ? <Check size={14} /> : <Copy size={14} />}
                        </button>

                        {/* Revoke */}
                        {isActive && (
                          <button
                            onClick={() => setConfirmRevoke(share)}
                            className="p-1.5 rounded-lg transition-colors"
                            style={{ color: 'var(--text-muted)', background: 'transparent' }}
                            title="Revogar link"
                            onMouseEnter={(e) => { e.currentTarget.style.color = '#f87171'; e.currentTarget.style.background = 'rgba(239,68,68,0.1)' }}
                            onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-muted)'; e.currentTarget.style.background = 'transparent' }}
                          >
                            <Trash2 size={14} />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Revoke confirmation dialog */}
      {confirmRevoke && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center"
          style={{ background: 'rgba(0,0,0,0.6)' }}
          onClick={(e) => { if (e.target === e.currentTarget) setConfirmRevoke(null) }}
        >
          <div
            className="w-full max-w-sm mx-4 p-5 rounded-xl"
            style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', boxShadow: '0 25px 50px rgba(0,0,0,0.5)' }}
          >
            <p className="text-sm font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
              Revogar link?
            </p>
            <p className="text-xs mb-4" style={{ color: 'var(--text-muted)', lineHeight: 1.6 }}>
              O link para <span className="font-mono" style={{ color: 'var(--text-secondary)' }}>{confirmRevoke.path.split('/').pop()}</span> será
              desativado imediatamente e não poderá mais ser acessado.
            </p>
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setConfirmRevoke(null)}
                className="px-3 py-1.5 text-sm rounded-lg"
                style={{ color: 'var(--text-secondary)', border: '1px solid var(--border)' }}
              >
                Cancelar
              </button>
              <button
                onClick={() => handleRevoke(confirmRevoke)}
                disabled={revoking === confirmRevoke.token}
                className="px-3 py-1.5 text-sm font-medium rounded-lg"
                style={{ background: 'rgba(239,68,68,0.15)', color: '#f87171', border: '1px solid rgba(239,68,68,0.3)' }}
              >
                {revoking === confirmRevoke.token ? 'Revogando...' : 'Revogar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
