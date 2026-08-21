import { Database, Sparkles } from 'lucide-react'

export default function Header() {
  return (
    <header className="h-14 shrink-0 flex items-center justify-between px-6 border-b border-white/[0.04] bg-[#09090b]/80 backdrop-blur-xl sticky top-0 z-50">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center">
          <Database className="w-4 h-4 text-white" strokeWidth={2.5} />
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-sm font-semibold text-white tracking-tight">Text</span>
          <span className="text-sm font-bold text-indigo-400">2</span>
          <span className="text-sm font-semibold text-white tracking-tight">SQL</span>
        </div>
      </div>
      <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.06]">
        <Sparkles className="w-3 h-3 text-amber-400" />
        <span className="text-xs text-zinc-400 font-medium">AI Powered</span>
      </div>
    </header>
  )
}
