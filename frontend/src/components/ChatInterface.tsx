import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, ChevronDown, ChevronUp } from 'lucide-react'

interface Source { text: string; source: string; score: number }
interface Message { role: 'user' | 'assistant'; content: string; sources?: Source[] }

interface Props { api: string }

export default function ChatInterface({ api }: Props) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [temperature, setTemperature] = useState(0.7)
  const [loading, setLoading] = useState(false)
  const [expandedSources, setExpandedSources] = useState<number[]>([])
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const send = async () => {
    if (!input.trim() || loading) return
    const query = input.trim()
    setInput('')
    setMessages((m) => [...m, { role: 'user', content: query }])
    setLoading(true)
    try {
      const res = await fetch(`${api}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, temperature }),
      })
      const data = await res.json()
      setMessages((m) => [...m, { role: 'assistant', content: data.answer, sources: data.sources }])
    } catch {
      setMessages((m) => [...m, { role: 'assistant', content: 'Error contacting backend. Is it running?' }])
    } finally {
      setLoading(false)
    }
  }

  const toggleSource = (i: number) =>
    setExpandedSources((s) => s.includes(i) ? s.filter((x) => x !== i) : [...s, i])

  return (
    <div className="bg-slate-800 rounded-xl flex flex-col h-[600px]">
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700">
        <span className="text-sm font-medium text-slate-300">Chat</span>
        <div className="flex items-center gap-3">
          <label className="text-xs text-slate-400">Temp: {temperature}</label>
          <input type="range" min={0} max={1.5} step={0.1} value={temperature}
            onChange={(e) => setTemperature(Number(e.target.value))}
            className="w-28 accent-indigo-500" />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <p className="text-slate-500 text-sm text-center mt-8">
            Upload a document, then ask anything about it.
          </p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'assistant' && <Bot size={18} className="text-indigo-400 mt-1 flex-shrink-0" />}
            <div className={`max-w-[80%] rounded-xl px-4 py-2 text-sm ${
              msg.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-slate-100'
            }`}>
              <p>{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2">
                  <button onClick={() => toggleSource(i)}
                    className="flex items-center gap-1 text-xs text-indigo-300 hover:text-indigo-200">
                    {expandedSources.includes(i) ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                    {msg.sources.length} source{msg.sources.length > 1 ? 's' : ''}
                  </button>
                  {expandedSources.includes(i) && (
                    <div className="mt-2 space-y-1">
                      {msg.sources.map((s, j) => (
                        <div key={j} className="bg-slate-800 rounded p-2 text-xs text-slate-300">
                          <span className="text-indigo-400 font-medium">{s.source}</span>
                          <span className="text-slate-500 ml-2">score: {s.score.toFixed(2)}</span>
                          <p className="mt-1 text-slate-400 line-clamp-2">{s.text}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
            {msg.role === 'user' && <User size={18} className="text-slate-400 mt-1 flex-shrink-0" />}
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
            <Bot size={18} className="text-indigo-400 mt-1" />
            <div className="bg-slate-700 rounded-xl px-4 py-2">
              <span className="animate-pulse text-slate-400 text-sm">Thinking…</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="p-4 border-t border-slate-700 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
          placeholder="Ask about your documents…"
          className="flex-1 bg-slate-700 rounded-lg px-4 py-2 text-sm text-slate-100 placeholder:text-slate-500 outline-none focus:ring-1 focus:ring-indigo-500"
        />
        <button onClick={send} disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors">
          <Send size={16} />
        </button>
      </div>
    </div>
  )
}
