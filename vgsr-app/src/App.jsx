import { useState, useCallback } from 'react'
import { Toaster } from 'react-hot-toast'
import SchemaInput from './components/SchemaInput'
import QueryPanel from './components/QueryPanel'
import Header from './components/Header'
import SchemaPreview from './components/SchemaPreview'
import HistoryPanel from './components/HistoryPanel'
import EmptyState from './components/EmptyState'

function App() {
  const [schema, setSchema] = useState(null)
  const [schemaText, setSchemaText] = useState('')
  const [history, setHistory] = useState([])

  const handleSchemaSubmit = useCallback((parsedSchema, raw) => {
    setSchema(parsedSchema)
    setSchemaText(raw)
  }, [])

  const handleQueryResult = useCallback((result) => {
    setHistory(prev => [result, ...prev].slice(0, 50))
  }, [])

  const handleClearSchema = useCallback(() => {
    setSchema(null)
    setSchemaText('')
  }, [])

  return (
    <div className="min-h-screen relative">
      <div className="ambient-glow" />

      <Toaster
        position="top-center"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#18181c',
            color: '#e4e4e7',
            border: '1px solid rgba(255,255,255,0.06)',
            borderRadius: '12px',
            fontSize: '13px',
            fontWeight: 500,
            boxShadow: '0 16px 48px -12px rgba(0,0,0,0.5)',
            padding: '12px 16px',
          },
          success: {
            iconTheme: { primary: '#10b981', secondary: '#18181c' },
          },
          error: {
            iconTheme: { primary: '#ef4444', secondary: '#18181c' },
          },
        }}
      />

      <div className="relative z-10 flex flex-col min-h-screen">
        <Header />

        {!schema ? (
          <main className="flex-1 flex items-center justify-center px-6 py-12">
            <div className="w-full max-w-2xl space-y-12 animate-fade-up">
              <EmptyState />
              <SchemaInput
                onSchemaSubmit={handleSchemaSubmit}
                schema={schema}
                onClear={handleClearSchema}
              />
            </div>
          </main>
        ) : (
          <main className="flex-1 flex gap-0 border-t border-white/[0.04]">
            {/* Left sidebar - Schema */}
            <aside className="w-[380px] shrink-0 border-r border-white/[0.04] flex flex-col animate-fade-in overflow-hidden">
              <SchemaInput
                onSchemaSubmit={handleSchemaSubmit}
                schema={schema}
                onClear={handleClearSchema}
              />
              <div className="flex-1 overflow-y-auto">
                <SchemaPreview schema={schema} />
              </div>
            </aside>

            {/* Main content - Query + History */}
            <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
              <div className="flex-1 p-6 space-y-6">
                <QueryPanel
                  schema={schema}
                  schemaText={schemaText}
                  onQueryResult={handleQueryResult}
                />
                <HistoryPanel history={history} />
              </div>
            </div>
          </main>
        )}
      </div>
    </div>
  )
}

export default App
