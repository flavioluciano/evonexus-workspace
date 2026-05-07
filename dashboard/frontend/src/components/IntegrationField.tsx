import { useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'

interface IntegrationFieldProps {
  label: string
  envKey: string
  value: string
  hint?: string
  required?: boolean
  hasError?: boolean
  onChange: (key: string, value: string) => void
}

const SENSITIVE_PATTERN = /SECRET|TOKEN|KEY|PASSWORD/i

function isSensitive(envKey: string): boolean {
  return SENSITIVE_PATTERN.test(envKey)
}

export default function IntegrationField({
  label,
  envKey,
  value,
  hint,
  required,
  hasError,
  onChange,
}: IntegrationFieldProps) {
  const [revealed, setRevealed] = useState(false)
  const sensitive = isSensitive(envKey)

  return (
    <div className="mb-4">
      {/* Label */}
      <div className="flex items-center gap-1.5 mb-1.5">
        <label
          htmlFor={envKey}
          className="text-sm font-medium text-[#e6edf3]"
        >
          {label}
        </label>
        {required && (
          <span className="text-xs text-[#EF4444]" aria-hidden="true">*</span>
        )}
        {!required && (
          <span className="text-xs text-[#667085]">(opcional)</span>
        )}
      </div>

      {/* Input wrapper */}
      <div className="relative">
        <input
          id={envKey}
          type={sensitive && !revealed ? 'password' : 'text'}
          value={value}
          onChange={(e) => onChange(envKey, e.target.value)}
          autoComplete="off"
          spellCheck={false}
          aria-required={required}
          aria-label={label}
          className={[
            'w-full rounded-lg px-3 py-2.5 text-sm font-mono',
            'bg-[#0C111D] border text-[#e6edf3]',
            'placeholder:text-[#3F3F46]',
            'focus:outline-none focus:ring-1',
            'transition-colors duration-150',
            sensitive ? 'pr-10' : '',
            hasError && required && !value
              ? 'border-red-500/50 focus:border-red-500/70 focus:ring-red-500/30'
              : 'border-[#21262d] focus:border-[#00FFA7]/40 focus:ring-[#00FFA7]/20',
          ].join(' ')}
          placeholder={sensitive ? '••••••••••••' : ''}
        />

        {sensitive && (
          <button
            type="button"
            onClick={() => setRevealed((v) => !v)}
            aria-label={revealed ? 'Ocultar valor' : 'Mostrar valor'}
            className="absolute inset-y-0 right-0 flex items-center px-3 text-[#667085] hover:text-[#e6edf3] transition-colors"
            tabIndex={-1}
          >
            {revealed ? <EyeOff size={15} /> : <Eye size={15} />}
          </button>
        )}
      </div>

      {/* Hint / error */}
      {hasError && required && !value && (
        <p className="mt-1 text-xs text-red-400">Campo obrigatório</p>
      )}
      {hint && !(hasError && required && !value) && (
        <p className="mt-1 text-xs text-[#667085]">{hint}</p>
      )}
    </div>
  )
}
