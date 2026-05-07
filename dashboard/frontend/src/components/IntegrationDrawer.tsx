import { useEffect, useRef, useState, useCallback } from 'react'
import { createPortal } from 'react-dom'
import { X, CheckCircle2, XCircle, Loader2, ExternalLink } from 'lucide-react'
import { api } from '../lib/api'
import { getIntegrationMeta } from '../lib/integrationMeta'
import IntegrationField from './IntegrationField'

interface DrawerIntegration {
  name: string
  type: string
  status: 'ok' | 'error' | 'pending'
  kind?: 'core' | 'custom'
  envKeys?: string[]
}

interface IntegrationDrawerProps {
  integration: DrawerIntegration | null
  envValues: Record<string, string>
  onClose: () => void
  onSaved?: () => void
}

type TestState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'ok'; message: string; latency: number }
  | { status: 'error'; message: string }

export default function IntegrationDrawer({
  integration,
  envValues,
  onClose,
  onSaved,
}: IntegrationDrawerProps) {
  const isOpen = integration !== null
  const meta = integration ? getIntegrationMeta(integration.name) : undefined

  // For custom integrations, synthesise fields from envKeys when meta is absent
  const effectiveFields = meta?.fields ?? (
    integration?.kind === 'custom' && integration.envKeys?.length
      ? integration.envKeys.map((key) => ({
          envKey: key,
          label: key,
          required: true,
          hint: undefined as string | undefined,
        }))
      : undefined
  )

  const [localValues, setLocalValues] = useState<Record<string, string>>({})
  const [showErrors, setShowErrors] = useState(false)
  const [saving, setSaving] = useState(false)
  const [testState, setTestState] = useState<TestState>({ status: 'idle' })

  const drawerRef = useRef<HTMLDivElement>(null)
  const firstFocusRef = useRef<HTMLButtonElement>(null)

  // Sync env values into local state when drawer opens
  useEffect(() => {
    if (!isOpen || !effectiveFields) return
    const initial: Record<string, string> = {}
    effectiveFields.forEach((f) => {
      initial[f.envKey] = envValues[f.envKey] ?? ''
    })
    setLocalValues(initial)
    setShowErrors(false)
    setTestState({ status: 'idle' })
  }, [isOpen, effectiveFields, envValues])

  // ESC key to close
  useEffect(() => {
    if (!isOpen) return
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [isOpen, onClose])

  // Focus trap — focus first focusable when opening
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => firstFocusRef.current?.focus(), 50)
    }
  }, [isOpen])

  // Focus trap tab cycling
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key !== 'Tab' || !drawerRef.current) return
      const focusable = drawerRef.current.querySelectorAll<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
      const first = focusable[0]
      const last = focusable[focusable.length - 1]
      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault()
          last?.focus()
        }
      } else {
        if (document.activeElement === last) {
          e.preventDefault()
          first?.focus()
        }
      }
    },
    []
  )

  const handleFieldChange = (key: string, value: string) => {
    setLocalValues((prev) => ({ ...prev, [key]: value }))
  }

  const hasRequiredErrors = (): boolean => {
    if (!effectiveFields) return false
    return effectiveFields.some((f) => f.required && !localValues[f.envKey]?.trim())
  }

  const handleSave = async () => {
    if (!effectiveFields) return
    setShowErrors(true)
    if (hasRequiredErrors()) return

    setSaving(true)
    try {
      // Build entries array with only the fields from this integration
      const entries = effectiveFields.map((f) => ({
        type: 'var' as const,
        key: f.envKey,
        value: localValues[f.envKey] ?? '',
      }))

      // Get current full env to merge into (don't overwrite unrelated vars)
      const current = await api.get('/config/env')
      const existingEntries: Array<{ type: string; key?: string; value?: string }> =
        current?.entries ?? []

      // Replace or append each key
      const updatedEntries = [...existingEntries]
      for (const newEntry of entries) {
        const idx = updatedEntries.findIndex(
          (e) => e.type === 'var' && e.key === newEntry.key
        )
        if (idx >= 0) {
          updatedEntries[idx] = newEntry
        } else {
          updatedEntries.push(newEntry)
        }
      }

      await api.put('/config/env', { entries: updatedEntries })
      onSaved?.()
      onClose()
    } catch {
      // keep open on error
    } finally {
      setSaving(false)
    }
  }

  const handleTest = async () => {
    if (!integration) return
    setTestState({ status: 'loading' })
    const t0 = performance.now()
    try {
      const result = await api.post(
        `/integrations/${encodeURIComponent(integration.name.toLowerCase().replace(/\s+/g, '-'))}/test`
      )
      const latency = Math.round(performance.now() - t0)
      if (result?.ok) {
        setTestState({ status: 'ok', message: result.message ?? 'Conexão OK', latency })
      } else {
        setTestState({ status: 'error', message: result?.error ?? 'Falha na conexão' })
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Erro ao testar conexão'
      setTestState({ status: 'error', message: msg })
    }
  }

  const isConnected = integration?.status === 'ok'

  const content = (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black/50 backdrop-blur-[2px] transition-opacity duration-300"
        style={{ opacity: isOpen ? 1 : 0, pointerEvents: isOpen ? 'auto' : 'none' }}
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer panel */}
      <div
        ref={drawerRef}
        role="dialog"
        aria-modal="true"
        aria-label={integration ? `Configurar ${integration.name}` : 'Configuração'}
        onKeyDown={handleKeyDown}
        className="fixed right-0 top-0 z-50 flex h-full w-full flex-col bg-[#0C111D] shadow-2xl transition-transform duration-300 ease-out sm:w-[400px]"
        style={{ transform: isOpen ? 'translateX(0)' : 'translateX(100%)' }}
      >
        {integration && (
          <>
            {/* Header */}
            <div className="flex items-start justify-between border-b border-[#21262d] px-5 py-4">
              <div className="flex items-center gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-base font-semibold text-[#e6edf3]">
                      {integration.name}
                    </h2>
                    <span
                      className="inline-block h-2 w-2 rounded-full shrink-0"
                      style={{
                        backgroundColor: isConnected ? '#00FFA7' : '#3F3F46',
                        boxShadow: isConnected ? '0 0 6px rgba(0,255,167,0.5)' : 'none',
                      }}
                    />
                  </div>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-xs text-[#667085] uppercase tracking-wider">
                      {integration.type}
                    </span>
                    <span className="text-xs text-[#667085]">
                      {isConnected ? '· Conectado' : '· Não configurado'}
                    </span>
                  </div>
                </div>
              </div>
              <button
                ref={firstFocusRef}
                type="button"
                onClick={onClose}
                aria-label="Fechar"
                className="p-1.5 rounded-lg text-[#667085] hover:text-[#e6edf3] hover:bg-[#21262d] transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            {/* Body */}
            <div className="flex-1 overflow-y-auto px-5 py-5">
              {meta?.description && (
                <p className="text-sm text-[#667085] mb-5">{meta.description}</p>
              )}

              {meta?.oauthFlow ? (
                /* OAuth integration */
                <div className="rounded-xl border border-[#21262d] bg-[#161b22] p-5 text-center">
                  <p className="text-sm text-[#667085] mb-1">
                    Esta integração usa autenticação OAuth.
                  </p>
                  <p className="text-xs text-[#3F3F46] mb-5">
                    Gerencie as contas na seção Social Accounts abaixo, ou conecte uma nova conta.
                  </p>
                  <a
                    href={`/connect/${integration.name.toLowerCase()}`}
                    className="inline-flex items-center gap-1.5 text-sm px-4 py-2 rounded-lg bg-[#00FFA7]/10 text-[#00FFA7] border border-[#00FFA7]/20 hover:bg-[#00FFA7]/20 transition-all"
                  >
                    <ExternalLink size={14} />
                    Conectar {integration.name}
                  </a>
                </div>
              ) : effectiveFields && effectiveFields.length > 0 ? (
                /* API key / custom integration fields */
                effectiveFields.map((field) => (
                  <IntegrationField
                    key={field.envKey}
                    label={field.label}
                    envKey={field.envKey}
                    value={localValues[field.envKey] ?? ''}
                    hint={field.hint}
                    required={field.required}
                    hasError={showErrors}
                    onChange={handleFieldChange}
                  />
                ))
              ) : (
                <p className="text-sm text-[#667085]">
                  Nenhuma configuração disponível para esta integração.
                </p>
              )}

              {meta?.docsUrl && (
                <a
                  href={meta.docsUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-[#667085] hover:text-[#00FFA7] transition-colors mt-2"
                >
                  <ExternalLink size={12} />
                  Documentação
                </a>
              )}
            </div>

            {/* Footer */}
            {!meta?.oauthFlow && effectiveFields && effectiveFields.length > 0 && (
              <div className="border-t border-[#21262d] px-5 py-4 space-y-3">
                {/* Test result */}
                {testState.status === 'ok' && (
                  <div className="flex items-center gap-2 text-xs text-[#00FFA7]">
                    <CheckCircle2 size={13} />
                    <span>{testState.message} · {testState.latency}ms</span>
                  </div>
                )}
                {testState.status === 'error' && (
                  <div className="flex items-center gap-2 text-xs text-red-400">
                    <XCircle size={13} />
                    <span>{testState.message}</span>
                  </div>
                )}

                {/* Action buttons */}
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={handleTest}
                    disabled={testState.status === 'loading' || !isConnected}
                    className="flex items-center gap-1.5 text-sm px-4 py-2 rounded-lg border border-[#21262d] text-[#667085] hover:text-[#e6edf3] hover:border-[#344054] transition-all disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    {testState.status === 'loading' ? (
                      <Loader2 size={14} className="animate-spin" />
                    ) : null}
                    Testar Conexão
                  </button>
                  <button
                    type="button"
                    onClick={handleSave}
                    disabled={saving}
                    className="flex-1 flex items-center justify-center gap-1.5 text-sm px-4 py-2 rounded-lg bg-[#00FFA7] text-[#0C111D] font-semibold hover:bg-[#00e699] transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                  >
                    {saving ? <Loader2 size={14} className="animate-spin" /> : null}
                    Salvar
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </>
  )

  return createPortal(content, document.body)
}
