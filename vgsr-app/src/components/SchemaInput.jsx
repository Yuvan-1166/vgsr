import { useState, useCallback, useRef, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import {
  Upload, Table2, Plus, X, FileJson, ClipboardPaste, Wand2,
  CheckCircle2, ChevronRight, Pencil
} from 'lucide-react'
import { parseSchema } from '../lib/schemaParser'

const INPUT_MODES = [
  { id: 'paste', label: 'Paste', icon: ClipboardPaste },
  { id: 'upload', label: 'Upload', icon: Upload },
  { id: 'visual', label: 'Builder', icon: Pencil },
]

export default function SchemaInput({ onSchemaSubmit, schema, onClear }) {
  const [mode, setMode] = useState('paste')
  const [rawInput, setRawInput] = useState('')

  function trySchemaParse(text) {
    try {
      const parsed = parseSchema(text)
      onSchemaSubmit(parsed, text)
      toast.success('Schema loaded')
    } catch (err) {
      toast.error(err.message || 'Could not parse schema')
    }
  }

  const trySchemaParseRef = useRef(trySchemaParse)
  useEffect(() => {
    trySchemaParseRef.current = trySchemaParse
  })

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length === 0) return
    const file = acceptedFiles[0]
    const reader = new FileReader()
    reader.onload = (e) => {
      const content = e.target.result
      setRawInput(content)
      trySchemaParseRef.current(content)
    }
    reader.readAsText(file)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.sql', '.txt', '.csv'],
      'application/json': ['.json'],
    },
    maxFiles: 1,
  })

  const handleSubmitPaste = () => {
    if (!rawInput.trim()) {
      toast.error('Enter a schema to continue')
      return
    }
    trySchemaParse(rawInput)
  }

  return (
    <div className="surface overflow-hidden">
      {/* Header */}
      <div className="px-5 py-3.5 flex items-center justify-between border-b border-white/[0.04]">
        <div className="flex items-center gap-2.5">
          <div className="relative">
            <div className={`w-2 h-2 rounded-full ${schema ? 'bg-emerald-400' : 'bg-zinc-600'}`} />
            {schema && (
              <div className="absolute inset-0 w-2 h-2 rounded-full bg-emerald-400 animate-ping opacity-30" />
            )}
          </div>
          <h2 className="text-sm font-medium text-zinc-200">
            {schema ? 'Schema loaded' : 'Database schema'}
          </h2>
        </div>
        {schema && (
          <button
            onClick={onClear}
            className="text-xs text-zinc-600 hover:text-red-400 transition-colors duration-150"
          >
            Reset
          </button>
        )}
      </div>

      {/* Mode Tabs */}
      <div className="flex border-b border-white/[0.04]">
        {INPUT_MODES.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setMode(id)}
            className={`flex-1 flex items-center justify-center gap-2 py-2.5 text-xs font-medium transition-all duration-150 border-b-2 -mb-px ${
              mode === id
                ? 'text-white border-indigo-500'
                : 'text-zinc-500 border-transparent hover:text-zinc-300'
            }`}
          >
            <Icon className="w-3.5 h-3.5" />
            {label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="p-5">
        {mode === 'paste' && (
          <PasteInput
            value={rawInput}
            onChange={setRawInput}
            onSubmit={handleSubmitPaste}
          />
        )}
        {mode === 'upload' && (
          <UploadInput
            getRootProps={getRootProps}
            getInputProps={getInputProps}
            isDragActive={isDragActive}
          />
        )}
        {mode === 'visual' && (
          <VisualBuilder onSchemaSubmit={onSchemaSubmit} />
        )}
      </div>

      {/* Success Banner */}
      {schema && (
        <div className="px-5 pb-5">
          <div className="rounded-xl bg-emerald-500/[0.06] border border-emerald-500/15 px-4 py-3 flex items-center gap-3">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <div className="flex-1 text-xs">
              <span className="text-emerald-300 font-medium">
                {schema.tables.length} table{schema.tables.length !== 1 ? 's' : ''}
              </span>
              <span className="text-emerald-500/50 mx-1.5">·</span>
              <span className="text-emerald-500/50">
                {schema.tables.reduce((acc, t) => acc + t.columns.length, 0)} columns
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function PasteInput({ value, onChange, onSubmit }) {
  return (
    <div className="space-y-3">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={`CREATE TABLE users (\n  id INT PRIMARY KEY,\n  name VARCHAR(100),\n  email VARCHAR(255)\n);`}
        className="w-full h-48 surface-inner rounded-xl px-4 py-3 text-sm text-zinc-300 placeholder-zinc-600 resize-none focus:outline-none focus:border-indigo-500/30 transition-colors font-mono leading-relaxed"
        spellCheck={false}
      />
      <button
        onClick={onSubmit}
        className="w-full py-2.5 bg-indigo-500 hover:bg-indigo-400 text-white text-sm font-medium rounded-xl transition-colors duration-150 flex items-center justify-center gap-2"
      >
        Load Schema
        <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  )
}

function UploadInput({ getRootProps, getInputProps, isDragActive }) {
  return (
    <div
      {...getRootProps()}
      className={`rounded-xl border-2 border-dashed p-10 text-center cursor-pointer transition-all duration-200 ${
        isDragActive
          ? 'border-indigo-500/50 bg-indigo-500/[0.04]'
          : 'border-white/[0.06] hover:border-white/[0.1] hover:bg-white/[0.01]'
      }`}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-3">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-colors ${
          isDragActive ? 'bg-indigo-500/15' : 'bg-white/[0.04]'
        }`}>
          {isDragActive ? (
            <FileJson className="w-6 h-6 text-indigo-400" />
          ) : (
            <Upload className="w-6 h-6 text-zinc-500" />
          )}
        </div>
        <div>
          <p className="text-sm text-zinc-300 font-medium mb-1">
            {isDragActive ? 'Release to upload' : 'Drag & drop a file'}
          </p>
          <p className="text-xs text-zinc-600">
            .sql, .json, .txt, .csv
          </p>
        </div>
      </div>
    </div>
  )
}

function VisualBuilder({ onSchemaSubmit }) {
  const [tables, setTables] = useState([
    { name: '', columns: [{ name: '', type: 'VARCHAR(255)', pk: false, nullable: true, fk: '' }] }
  ])

  const addTable = () => {
    setTables([...tables, { name: '', columns: [{ name: '', type: 'VARCHAR(255)', pk: false, nullable: true, fk: '' }] }])
  }

  const removeTable = (idx) => {
    if (tables.length <= 1) return
    setTables(tables.filter((_, i) => i !== idx))
  }

  const updateTable = (idx, field, value) => {
    const updated = [...tables]
    updated[idx] = { ...updated[idx], [field]: value }
    setTables(updated)
  }

  const addColumn = (tableIdx) => {
    const updated = [...tables]
    updated[tableIdx].columns.push({ name: '', type: 'VARCHAR(255)', pk: false, nullable: true, fk: '' })
    setTables(updated)
  }

  const removeColumn = (tableIdx, colIdx) => {
    if (tables[tableIdx].columns.length <= 1) return
    const updated = [...tables]
    updated[tableIdx].columns = updated[tableIdx].columns.filter((_, i) => i !== colIdx)
    setTables(updated)
  }

  const updateColumn = (tableIdx, colIdx, field, value) => {
    const updated = [...tables]
    updated[tableIdx].columns[colIdx] = {
      ...updated[tableIdx].columns[colIdx],
      [field]: value,
    }
    setTables(updated)
  }

  const handleSubmit = () => {
    const validTables = tables.filter(t => t.name.trim())
    if (validTables.length === 0) {
      toast.error('Add at least one table with a name')
      return
    }
    for (const t of validTables) {
      const validCols = t.columns.filter(c => c.name.trim())
      if (validCols.length === 0) {
        toast.error(`Table "${t.name}" needs at least one column`)
        return
      }
    }

    const sql = validTables.map(t => {
      const cols = t.columns
        .filter(c => c.name.trim())
        .map(c => {
          let def = `  ${c.name} ${c.type}`
          if (c.pk) def += ' PRIMARY KEY'
          if (!c.nullable && !c.pk) def += ' NOT NULL'
          if (c.fk) def += ` REFERENCES ${c.fk}`
          return def
        })
        .join(',\n')
      return `CREATE TABLE ${t.name} (\n${cols}\n);`
    }).join('\n\n')

    try {
      const parsed = parseSchema(sql)
      onSchemaSubmit(parsed, sql)
      toast.success('Schema built')
    } catch (err) {
      toast.error(err.message)
    }
  }

  const SQL_TYPES = [
    'INT', 'BIGINT', 'SMALLINT', 'TINYINT',
    'VARCHAR(255)', 'VARCHAR(100)', 'VARCHAR(50)', 'TEXT', 'CHAR(1)',
    'DECIMAL(10,2)', 'FLOAT', 'DOUBLE',
    'BOOLEAN', 'BIT',
    'DATE', 'DATETIME', 'TIMESTAMP',
    'BLOB', 'JSON', 'UUID',
  ]

  return (
    <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
      {tables.map((table, ti) => (
        <div key={ti} className="surface-inner p-3 space-y-2 animate-fade-in">
          <div className="flex items-center gap-2">
            <Table2 className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
            <input
              value={table.name}
              onChange={(e) => updateTable(ti, 'name', e.target.value)}
              placeholder="table_name"
              className="flex-1 bg-transparent border border-white/[0.06] rounded-lg px-3 py-1.5 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-indigo-500/30 transition-colors font-mono"
            />
            {tables.length > 1 && (
              <button
                onClick={() => removeTable(ti)}
                className="p-1 text-zinc-600 hover:text-red-400 transition-colors"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          <div className="space-y-1.5 pl-6">
            {table.columns.map((col, ci) => (
              <div key={ci} className="flex items-center gap-1.5 group/col">
                <input
                  value={col.name}
                  onChange={(e) => updateColumn(ti, ci, 'name', e.target.value)}
                  placeholder="column"
                  className="w-[30%] bg-transparent border border-white/[0.05] rounded-lg px-2.5 py-1.5 text-xs text-white/90 placeholder-zinc-600 focus:outline-none focus:border-indigo-500/30 transition-colors font-mono"
                />
                <input
                  value={col.type}
                  onChange={(e) => updateColumn(ti, ci, 'type', e.target.value)}
                  className="w-[25%] bg-transparent border border-white/[0.05] rounded-lg px-2.5 py-1.5 text-xs text-indigo-300/70 focus:outline-none focus:border-indigo-500/30 transition-colors font-mono"
                  list={`types-${ti}-${ci}`}
                />
                <datalist id={`types-${ti}-${ci}`}>
                  {SQL_TYPES.map(t => <option key={t} value={t} />)}
                </datalist>
                <label className="flex items-center gap-1 px-1 py-1 rounded cursor-pointer select-none hover:bg-white/[0.03] transition-colors">
                  <input
                    type="checkbox"
                    checked={col.pk}
                    onChange={(e) => updateColumn(ti, ci, 'pk', e.target.checked)}
                    className="accent-indigo-500 w-3 h-3 rounded"
                  />
                  <span className="text-[10px] text-amber-400/70 font-semibold">PK</span>
                </label>
                <label className="flex items-center gap-1 px-1 py-1 rounded cursor-pointer select-none hover:bg-white/[0.03] transition-colors">
                  <input
                    type="checkbox"
                    checked={col.nullable}
                    onChange={(e) => updateColumn(ti, ci, 'nullable', e.target.checked)}
                    className="accent-indigo-500 w-3 h-3 rounded"
                  />
                  <span className="text-[10px] text-zinc-600 font-medium">NUL</span>
                </label>
                {table.columns.length > 1 && (
                  <button
                    onClick={() => removeColumn(ti, ci)}
                    className="p-0.5 text-zinc-700 hover:text-red-400 transition-colors opacity-0 group-hover/col:opacity-100"
                  >
                    <X className="w-3 h-3" />
                  </button>
                )}
              </div>
            ))}
          </div>

          <button
            onClick={() => addColumn(ti)}
            className="flex items-center gap-1.5 text-xs text-indigo-400/60 hover:text-indigo-400 transition-colors pl-6 mt-1"
          >
            <Plus className="w-3 h-3" /> Add column
          </button>
        </div>
      ))}

      <button
        onClick={addTable}
        className="w-full py-2.5 border border-dashed border-white/[0.06] rounded-xl text-xs text-zinc-500 hover:text-indigo-400 hover:border-indigo-500/25 transition-all duration-150 flex items-center justify-center gap-1.5"
      >
        <Plus className="w-3.5 h-3.5" /> Add table
      </button>

      <button
        onClick={handleSubmit}
        className="w-full py-2.5 bg-indigo-500 hover:bg-indigo-400 text-white text-sm font-medium rounded-xl transition-colors duration-150 flex items-center justify-center gap-2"
      >
        <Wand2 className="w-4 h-4" />
        Build Schema
      </button>
    </div>
  )
}
