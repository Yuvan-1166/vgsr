import { ArrowRight, Database, MessageSquareText, Zap } from 'lucide-react'

export default function EmptyState() {
  return (
    <div className="text-center space-y-8">
      <div className="space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-xs font-medium text-indigo-400 tracking-wide uppercase">
          <Zap className="w-3 h-3" />
          AI-Powered SQL Generation
        </div>

        <h1 className="text-4xl sm:text-5xl font-bold text-white tracking-tight leading-[1.1]">
          Ask questions.
          <br />
          <span className="text-zinc-500">Get SQL.</span>
        </h1>

        <p className="text-zinc-500 text-base max-w-md mx-auto leading-relaxed">
          Describe what you need in plain English, get optimized production-ready SQL queries.
        </p>
      </div>

      <div className="flex items-center justify-center gap-8 text-sm text-zinc-500">
        <Step num="1" icon={Database} color="indigo" text="Load schema" />
        <ArrowRight className="w-4 h-4 text-zinc-700" />
        <Step num="2" icon={MessageSquareText} color="violet" text="Ask in English" />
        <ArrowRight className="w-4 h-4 text-zinc-700" />
        <Step num="3" icon={Zap} color="emerald" text="Get SQL" />
      </div>
    </div>
  )
}

function Step({ num, icon: Icon, color, text }) {
  const colors = {
    indigo: 'bg-indigo-500/10 text-indigo-400',
    violet: 'bg-violet-500/10 text-violet-400',
    emerald: 'bg-emerald-500/10 text-emerald-400',
  }

  return (
    <div className="flex items-center gap-3">
      <div className={`w-9 h-9 rounded-xl ${colors[color]} flex items-center justify-center`}>
        <Icon className="w-4 h-4" />
      </div>
      <div className="text-left">
        <span className="text-[10px] font-mono text-zinc-600 block">Step {num}</span>
        <span className="font-medium text-zinc-300">{text}</span>
      </div>
    </div>
  )
}
