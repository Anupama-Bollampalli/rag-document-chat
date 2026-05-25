import { useState } from 'react'
import { FileText, Thermometer } from 'lucide-react'
import ChatInterface from './components/ChatInterface'
import DocumentUploader from './components/DocumentUploader'
import TemperatureStudy from './components/TemperatureStudy'

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function App() {
  const [tab, setTab] = useState<'chat' | 'temp'>('chat')
  const [docs, setDocs] = useState<string[]>([])

  const refreshDocs = async () => {
    const res = await fetch(`${API}/documents`)
    const data = await res.json()
    setDocs(data.documents)
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <header className="border-b border-slate-700 px-6 py-4 flex items-center gap-3">
        <FileText className="text-indigo-400" size={24} />
        <h1 className="text-xl font-bold text-white">RAG Document Chat</h1>
        <span className="ml-2 text-xs bg-indigo-900 text-indigo-300 px-2 py-0.5 rounded-full">
          sentence-transformers · ChromaDB
        </span>
      </header>

      <div className="max-w-6xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <DocumentUploader api={API} onUploaded={refreshDocs} docs={docs} />
        </div>

        <div className="lg:col-span-3">
          <div className="flex gap-2 mb-4">
            {([['chat', <FileText size={14} />, 'Chat'], ['temp', <Thermometer size={14} />, 'Temperature Study']] as const).map(
              ([id, icon, label]) => (
                <button
                  key={id}
                  onClick={() => setTab(id as 'chat' | 'temp')}
                  className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    tab === id ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                  }`}
                >
                  {icon}{label}
                </button>
              )
            )}
          </div>

          {tab === 'chat' ? (
            <ChatInterface api={API} />
          ) : (
            <TemperatureStudy api={API} />
          )}
        </div>
      </div>
    </div>
  )
}
