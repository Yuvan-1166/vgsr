import { useState } from 'react'
import { Table2, Key, Link2, Hash, Type, Calendar, ToggleLeft, ChevronDown, ChevronUp } from 'lucide-react'

function getColIcon(type) {
  const t = type.toUpperCase()
  if (t.includes('INT') || t.includes('BIGINT') || t.includes('SMALLINT') || t.includes('TINYINT')) return Hash
  if (t.includes('VARCHAR') || t.includes('TEXT') || t.includes('CHAR') || t.includes('JSON')) return Type
  if (t.includes('DATE') || t.includes('TIME') || t.includes('TIMESTAMP')) return Calendar
  if (t.includes('BOOL') || t.includes('BIT')) return ToggleLeft
  return Type
}

function getColColor(type) {
  const t = type.toUpperCase()
  if (t.includes('INT') || t.includes('BIGINT')) return 'text-amber-400/70'
  if (t.includes('VARCHAR') || t.includes('TEXT')) return 'text-sky-400/70'
  if (t.includes('DECIMAL') || t.includes('FLOAT') || t.includes('DOUBLE')) return 'text-emerald-400/70'
  if (t.includes('DATE') || t.includes('TIME')) return 'text-violet-400/70'
  if (t.includes('BOOL')) return 'text-rose-400/70'
  return 'text-zinc-400/70'
}

export default function SchemaPreview({ schema }) {
  const [collapsed, setCollapsed] = useState({})

  if (!schema?.tables?.length) return null

  const toggleTable = (name) => {
    setCollapsed(prev => ({ ...prev, [name]: !prev[name] }))
  }

  return (
    <div className="border-b border-white/[0.04]">
      <div className="px-5 py-3 flex items-center justify-between border-b border-white/[0.04]">
        <div className="flex items-center gap-2.5">
          <Table2 className="w-3.5 h-3.5 text-zinc-500" />
          <span className="text-xs font-medium text-zinc-400">Schema</span>
        </div>
        <span className="text-[10px] text-zinc-600 font-mono">
          {schema.tables.length} tables
        </span>
      </div>

      <div className="divide-y divide-white/[0.03]">
        {schema.tables.map((table) => {
          const isCollapsed = collapsed[table.name]
          return (
            <div key={table.name}>
              <button
                onClick={() => toggleTable(table.name)}
                className="w-full px-5 py-2.5 flex items-center gap-2.5 text-left hover:bg-white/[0.02] transition-colors group"
              >
                <Table2 className="w-3.5 h-3.5 text-indigo-400/70 shrink-0" />
                <span className="text-xs font-medium text-indigo-300/80 font-mono flex-1">{table.name}</span>
                <span className="text-[10px] text-zinc-600 font-mono">{table.columns.length}</span>
                {isCollapsed ? (
                  <ChevronDown className="w-3 h-3 text-zinc-600" />
                ) : (
                  <ChevronUp className="w-3 h-3 text-zinc-600" />
                )}
              </button>

              {!isCollapsed && (
                <div className="bg-white/[0.01]">
                  {table.columns.map((col) => {
                    const Icon = getColIcon(col.type)
                    const colorClass = getColColor(col.type)
                    return (
                      <div
                        key={col.name}
                        className="px-5 py-2 flex items-center gap-2.5 text-xs pl-10"
                      >
                        <Icon className={`w-3 h-3 shrink-0 ${colorClass}`} />
                        <span className="text-zinc-300 font-mono flex-1">{col.name}</span>
                        <span className={`font-mono text-[11px] ${colorClass}`}>{col.type}</span>
                        <div className="flex items-center gap-1 ml-1">
                          {col.pk && (
                            <span className="flex items-center gap-0.5 px-1 py-0.5 rounded bg-amber-500/10 text-amber-400">
                              <Key className="w-2.5 h-2.5" />
                              <span className="text-[9px] font-bold">PK</span>
                            </span>
                          )}
                          {col.fk && (
                            <span className="flex items-center gap-0.5 px-1 py-0.5 rounded bg-cyan-500/10 text-cyan-400">
                              <Link2 className="w-2.5 h-2.5" />
                              <span className="text-[9px] font-bold">FK</span>
                            </span>
                          )}
                          {!col.nullable && !col.pk && (
                            <span className="text-[9px] font-semibold text-zinc-600">NN</span>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
