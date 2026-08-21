import { useState } from 'react'
import { format } from 'sql-formatter'
import { Clock, Copy, Check, ChevronDown, ChevronUp, MessageSquareText } from 'lucide-react'

export default function HistoryPanel({ history }) {
  if (!history.length) return null

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Clock className="w-3.5 h-3.5 text-zinc-500" />
          <span className="text-xs font-medium text-zinc-400">History</span>
        </div>
        <span className="text-[10px] text-zinc-600 font-mono">
          {history.length} query{history.length !== 1 ? 'ies' : ''}
        </span>
      </div>

      <div className="space-y-1">
        {history.map((item, i) => (
          <HistoryItem key={i} item={item} />
        ))}
      </div>
    </div>
  )
}

function HistoryItem({ item }) {
  const [expanded, setExpanded] = useState(false)
  const [copied, setCopied] = useState(false)

  let formattedSQL = item.sql
  try {
    formattedSQL = format(item.sql, { language: 'sql' })
  } catch {}

  const copySQL = (e) => {
    e.stopPropagation()
    navigator.clipboard.writeText(item.sql)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const timeStr = item.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

  return (
    <div className="surface rounded-xl overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-4 py-3 flex items-center gap-3 text-left hover:bg-white/[0.02] transition-colors"
      >
        <MessageSquareText className="w-3.5 h-3.5 text-zinc-600 shrink-0" />
        <span className="text-xs text-zinc-400 flex-1 truncate">{item.question}</span>
        <span className="text-[10px] text-zinc-600 font-mono shrink-0">{timeStr}</span>
        {expanded ? (
          <ChevronUp className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
        ) : (
          <ChevronDown className="w-3.5 h-3.5 text-zinc-600 shrink-0" />
        )}
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-3 border-t border-white/[0.04] pt-3 animate-slide-down">
          <div className="surface-inner p-3 flex items-start justify-between gap-3">
            <pre className="text-xs text-zinc-400 overflow-x-auto font-mono leading-relaxed flex-1">
              <code>{formattedSQL}</code>
            </pre>
            <button
              onClick={copySQL}
              className="shrink-0 p-1.5 rounded-lg text-zinc-600 hover:text-indigo-400 hover:bg-indigo-500/10 transition-all"
            >
              {copied ? (
                <Check className="w-3.5 h-3.5 text-emerald-400" />
              ) : (
                <Copy className="w-3.5 h-3.5" />
              )}
            </button>
          </div>
          {item.explanation && (
            <p className="text-[11px] text-zinc-500 leading-relaxed">{item.explanation}</p>
          )}
        </div>
      )}
    </div>
  )
}
