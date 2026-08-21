import { useState, useRef, useEffect } from 'react'
import toast from 'react-hot-toast'
import { Send, Loader2, Copy, Check, Sparkles, AlertCircle, RotateCcw, BookOpen } from 'lucide-react'
import { format } from 'sql-formatter'
import { generateSQL } from '../lib/groqClient'

export default function QueryPanel({ schema, schemaText, onQueryResult }) {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [copied, setCopied] = useState(false)
  const textareaRef = useRef()

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px'
    }
  }, [question])

  const handleSubmit = async () => {
    if (!schema) {
      toast.error('Load a schema first')
      return
    }
    if (!question.trim()) {
      toast.error('Enter a question')
      return
    }

    setLoading(true)
    setResult(null)

    try {
      const response = await generateSQL(schemaText, question)
      setResult(response)
      onQueryResult({
        question,
        sql: response.sql,
        explanation: response.explanation,
        timestamp: new Date(),
      })
    } catch (err) {
      toast.error(err.message || 'Failed to generate SQL')
      setResult({
        sql: '',
        explanation: '',
        error: err.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const copySQL = () => {
    if (result?.sql) {
      navigator.clipboard.writeText(result.sql)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  let formattedSQL = result?.sql || ''
  try {
    if (formattedSQL) {
      formattedSQL = format(formattedSQL, { language: 'sql' })
    }
  } catch {}

  const suggestions = [
    'Show all users with their order counts',
    'Find the top 5 products by revenue',
    'List active users who signed up this month',
  ]

  return (
    <div className="space-y-4">
      {/* Input */}
      <div className="relative group">
        <div className="absolute top-4 left-4">
          <Sparkles className="w-4 h-4 text-indigo-400/50" />
        </div>
        <textarea
          ref={textareaRef}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={schema ? "Ask a question about your data..." : "Load a schema first, then ask your question..."}
          disabled={!schema}
          className="w-full min-h-[80px] max-h-[200px] surface rounded-2xl pl-10 pr-20 py-4 text-sm text-zinc-200 placeholder-zinc-600 resize-none focus:outline-none focus:border-indigo-500/30 transition-colors duration-150 disabled:opacity-30 disabled:cursor-not-allowed"
          spellCheck={false}
        />
        <div className="absolute bottom-3 right-3 flex items-center gap-2">
          <span className="text-[10px] text-zinc-700 font-mono opacity-0 group-hover:opacity-100 transition-opacity">
            {navigator.platform?.includes('Mac') ? '⌘' : 'Ctrl'}+Enter
          </span>
          <button
            onClick={handleSubmit}
            disabled={loading || !schema || !question.trim()}
            className="w-8 h-8 rounded-xl bg-indigo-500 hover:bg-indigo-400 disabled:bg-zinc-800 disabled:cursor-not-allowed text-white flex items-center justify-center transition-colors duration-150 active:scale-95"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {/* Suggestions */}
      {!question && !result && schema && (
        <div className="flex flex-wrap gap-2">
          {suggestions.map((s) => (
            <button
              key={s}
              onClick={() => setQuestion(s)}
              className="px-3 py-1.5 rounded-lg bg-white/[0.03] border border-white/[0.05] text-xs text-zinc-500 hover:text-indigo-400 hover:border-indigo-500/20 transition-all duration-150"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="surface rounded-2xl overflow-hidden animate-fade-in">
          <div className="px-5 py-3 border-b border-white/[0.04] flex items-center gap-2">
            <Loader2 className="w-3.5 h-3.5 text-indigo-400 animate-spin" />
            <span className="text-xs text-zinc-500 font-medium">Generating SQL...</span>
          </div>
          <div className="p-5 space-y-3">
            <div className="h-3 w-3/4 rounded-md shimmer" />
            <div className="h-3 w-1/2 rounded-md shimmer" />
            <div className="h-3 w-5/6 rounded-md shimmer" />
            <div className="h-3 w-2/3 rounded-md shimmer" />
          </div>
        </div>
      )}

      {/* Result */}
      {result && !result.error && result.sql && (
        <div className="space-y-3 animate-slide-down">
          <div className="surface rounded-2xl overflow-hidden">
            <div className="px-5 py-3 border-b border-white/[0.04] flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
                <span className="text-xs text-zinc-500 font-medium uppercase tracking-wider">Generated SQL</span>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => { setResult(null); setQuestion('') }}
                  className="p-1.5 rounded-lg text-zinc-600 hover:text-zinc-300 hover:bg-white/[0.05] transition-all"
                  title="New query"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={copySQL}
                  className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-zinc-500 hover:text-indigo-400 hover:bg-indigo-500/10 transition-all duration-150"
                >
                  {copied ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-emerald-400">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>
            </div>
            <div className="relative">
              <pre className="p-5 text-sm text-zinc-300 overflow-x-auto leading-relaxed">
                <code>{colorizeSQL(formattedSQL)}</code>
              </pre>
            </div>
          </div>

          {result.explanation && (
            <div className="rounded-xl bg-violet-500/[0.05] border border-violet-500/10 px-4 py-3 flex items-start gap-2.5">
              <BookOpen className="w-3.5 h-3.5 text-violet-400 mt-0.5 shrink-0" />
              <p className="text-xs text-violet-300/70 leading-relaxed">{result.explanation}</p>
            </div>
          )}
        </div>
      )}

      {/* Error */}
      {result?.error && (
        <div className="rounded-xl bg-red-500/[0.05] border border-red-500/10 px-4 py-3 flex items-start gap-2.5 animate-slide-down">
          <AlertCircle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
          <div>
            <p className="text-xs text-red-300 font-medium mb-0.5">Generation failed</p>
            <p className="text-[11px] text-red-400/50">{result.error}</p>
          </div>
        </div>
      )}
    </div>
  )
}

function colorizeSQL(sql) {
  if (!sql) return null

  const keywords = /\b(SELECT|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|OUTER|ON|AND|OR|NOT|IN|AS|GROUP|BY|ORDER|HAVING|LIMIT|OFFSET|INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|TABLE|DROP|ALTER|INDEX|UNION|ALL|DISTINCT|COUNT|SUM|AVG|MIN|MAX|CASE|WHEN|THEN|ELSE|END|BETWEEN|LIKE|IS|NULL|EXISTS|WITH|OVER|PARTITION|ROW_NUMBER|RANK|DENSE_RANK|FETCH|NEXT|ROWS|ONLY|FIRST|LAST|ASC|DESC|CASE|LIKE|ANY|SOME|INTERSECT|EXCEPT|MINUS|CROSS|NATURAL|FULL|USING|Grant|REVOKE|COMMIT|ROLLBACK|BEGIN|TRANSACTION|PRIMARY|KEY|FOREIGN|REFERENCES|CONSTRAINT|DEFAULT|CHECK|UNIQUE)\b/gi

  const parts = []
  let lastIndex = 0

  let match
  const regex = new RegExp(keywords.source, 'gi')
  while ((match = regex.exec(sql)) !== null) {
    if (match.index > lastIndex) {
      parts.push(<span key={`t${lastIndex}`}>{sql.slice(lastIndex, match.index)}</span>)
    }
    parts.push(
      <span key={`k${match.index}`} className="sql-keyword">
        {match[0]}
      </span>
    )
    lastIndex = regex.lastIndex
  }
  if (lastIndex < sql.length) {
    parts.push(<span key={`e${lastIndex}`}>{sql.slice(lastIndex, sql.length)}</span>)
  }

  return parts
}
