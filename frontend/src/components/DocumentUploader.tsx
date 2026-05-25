import { useState, useRef } from 'react'
import { Upload, FileText, CheckCircle } from 'lucide-react'

interface Props { api: string; onUploaded: () => void; docs: string[] }

export default function DocumentUploader({ api, onUploaded, docs }: Props) {
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const upload = async (file: File) => {
    setUploading(true)
    setMessage('')
    const form = new FormData()
    form.append('file', file)
    try {
      const res = await fetch(`${api}/upload`, { method: 'POST', body: form })
      const data = await res.json()
      setMessage(data.message || 'Uploaded!')
      onUploaded()
    } catch {
      setMessage('Upload failed — is the backend running?')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="bg-slate-800 rounded-xl p-4 space-y-4">
      <h2 className="font-semibold text-slate-200">Documents</h2>

      <div
        className="border-2 border-dashed border-slate-600 rounded-lg p-6 text-center cursor-pointer hover:border-indigo-500 transition-colors"
        onClick={() => inputRef.current?.click()}
      >
        <Upload className="mx-auto mb-2 text-slate-400" size={24} />
        <p className="text-xs text-slate-400">Click to upload .txt or .pdf</p>
        <input ref={inputRef} type="file" accept=".txt,.pdf" className="hidden"
          onChange={(e) => { if (e.target.files?.[0]) upload(e.target.files[0]) }} />
      </div>

      {uploading && <p className="text-xs text-indigo-400 animate-pulse">Processing…</p>}
      {message && <p className="text-xs text-emerald-400">{message}</p>}

      {docs.length > 0 && (
        <div className="space-y-1">
          <p className="text-xs text-slate-500 uppercase tracking-wide">Indexed</p>
          {docs.map((d) => (
            <div key={d} className="flex items-center gap-2 text-xs text-slate-300">
              <CheckCircle size={12} className="text-emerald-400" />
              <span className="truncate">{d}</span>
            </div>
          ))}
        </div>
      )}

      {docs.length === 0 && !uploading && (
        <div className="text-xs text-slate-500 space-y-1 pt-2">
          <p className="font-medium">No documents yet.</p>
          <p>Upload a PDF or text file to start chatting with your documents.</p>
        </div>
      )}
    </div>
  )
}
