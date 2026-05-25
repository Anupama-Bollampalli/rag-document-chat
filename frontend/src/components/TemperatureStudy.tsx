import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Thermometer, Play } from 'lucide-react'

interface TempResult {
  temperature: number
  answer: string
  metrics: { word_count: number; unique_word_ratio: number; sentence_count: number }
}

interface Props { api: string }

const COLORS = ['#6366f1', '#22d3ee', '#f59e0b', '#ec4899']

export default function TemperatureStudy({ api }: Props) {
  const [query, setQuery] = useState('What are the main ideas in this document?')
  const [results, setResults] = useState<TempResult[]>([])
  const [loading, setLoading] = useState(false)

  const run = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${api}/temperature-study`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      })
      const data = await res.json()
      setResults(data.results)
    } catch {
      alert('Error contacting backend. Is it running?')
    } finally {
      setLoading(false)
    }
  }

  const chartData = results.map((r) => ({
    temp: `T=${r.temperature}`,
    words: r.metrics.word_count,
    unique_ratio: Math.round(r.metrics.unique_word_ratio * 100),
  }))

  return (
    <div className="space-y-4">
      <div className="bg-slate-800 rounded-xl p-4">
        <div className="flex items-center gap-2 mb-3">
          <Thermometer className="text-amber-400" size={18} />
          <h2 className="font-semibold text-slate-200">Temperature Effect Study</h2>
        </div>
        <p className="text-xs text-slate-400 mb-4">
          See how LLM temperature (0.0 → 1.5) affects response style on the same query.
          Low temperature = precise & factual. High temperature = creative & verbose.
        </p>
        <div className="flex gap-2">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 bg-slate-700 rounded-lg px-4 py-2 text-sm text-slate-100 outline-none focus:ring-1 focus:ring-indigo-500"
            placeholder="Enter a query to study…"
          />
          <button onClick={run} disabled={loading}
            className="flex items-center gap-2 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm transition-colors">
            <Play size={14} />{loading ? 'Running…' : 'Run Study'}
          </button>
        </div>
      </div>

      {results.length > 0 && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {results.map((r, i) => (
              <div key={r.temperature} className="bg-slate-800 rounded-xl p-4 border-t-2"
                style={{ borderColor: COLORS[i] }}>
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium text-sm" style={{ color: COLORS[i] }}>
                    Temperature {r.temperature}
                  </span>
                  <span className="text-xs text-slate-500">
                    {r.metrics.word_count} words · {Math.round(r.metrics.unique_word_ratio * 100)}% unique
                  </span>
                </div>
                <p className="text-sm text-slate-300 leading-relaxed">{r.answer}</p>
              </div>
            ))}
          </div>

          <div className="bg-slate-800 rounded-xl p-4">
            <h3 className="text-sm font-semibold text-slate-300 mb-4">Response Metrics Comparison</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={chartData}>
                <XAxis dataKey="temp" stroke="#94a3b8" tick={{ fontSize: 12 }} />
                <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }} />
                <Legend />
                <Bar dataKey="words" fill="#6366f1" name="Word Count" radius={[4,4,0,0]} />
                <Bar dataKey="unique_ratio" fill="#22d3ee" name="Unique Word %" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  )
}
