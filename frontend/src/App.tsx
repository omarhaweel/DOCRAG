import { type FormEvent, useCallback, useRef, useState } from 'react'
import './App.css'

type AskResponse = {
  answer?: unknown
}

function formatAnswer(value: unknown): string {
  if (typeof value === 'string') return value
  if (value == null) return ''
  try {
    return JSON.stringify(value, null, 2)
  } catch {
    return String(value)
  }
}

/** API returns `{ answer: string }` or `{ answer: { result: string, ... } }` from LangChain */
function textFromAskResponseBody(data: unknown): string {
  if (!data || typeof data !== 'object') return ''
  const answer = (data as AskResponse).answer
  if (typeof answer === 'string') return answer
  if (answer && typeof answer === 'object' && 'result' in answer) {
    const r = (answer as { result: unknown }).result
    if (typeof r === 'string') return r
  }
  return formatAnswer(answer)
}

/** Dev: Vite proxy `/api` → backend. Override with VITE_API_URL e.g. http://127.0.0.1:8000 */
function apiBase(): string {
  const raw = import.meta.env.VITE_API_URL
  if (raw && String(raw).trim()) {
    return String(raw).replace(/\/$/, '')
  }
  return '/api'
}

export default function App() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<
    { role: 'user' | 'assistant'; text: string }[]
  >([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const listRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = useCallback(() => {
    requestAnimationFrame(() => {
      const el = listRef.current
      if (el) el.scrollTop = el.scrollHeight
    })
  }, [])

  const send = async (e?: FormEvent) => {
    e?.preventDefault()
    const q = input.trim()
    if (!q || loading) return

    setInput('')
    setError(null)
    setMessages((m) => [...m, { role: 'user', text: q }])
    scrollToBottom()
    setLoading(true)

    try {
      const res = await fetch(`${apiBase()}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q }),
      })

      if (!res.ok) {
        const t = await res.text()
        throw new Error(t || `Request failed (${res.status})`)
      }

      const data = (await res.json()) as AskResponse
      const text = textFromAskResponseBody(data)
      setMessages((m) => [...m, { role: 'assistant', text }])
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Something went wrong'
      setError(msg)
      setMessages((m) => [
        ...m,
        {
          role: 'assistant',
          text: `Could not reach the server. ${msg}`,
        },
      ])
    } finally {
      setLoading(false)
      scrollToBottom()
    }
  }

  return (
    <div className="shell">
      <header className="header">
        <h1 className="title">Ask your documents</h1>
      </header>

      <main className="panel" aria-live="polite">
        <div className="messages" ref={listRef}>
          {messages.length === 0 ? (
            <p className="empty">Ask a question to get an answer from your Documents.</p>
          ) : (
            messages.map((m, i) => (
              <div
                key={i}
                className={`bubble ${m.role === 'user' ? 'user' : 'assistant'}`}
              >
                <span className="role">{m.role === 'user' ? 'You' : 'Answer'}</span>
                <div className="text">{m.text}</div>
              </div>
            ))
          )}
          {loading && (
            <div className="bubble assistant thinking">
              <span className="role">Answer</span>
              <div className="dots" aria-hidden>
                <span /><span /><span />
              </div>
            </div>
          )}
        </div>

        <form className="composer" onSubmit={send}>
          <label className="sr-only" htmlFor="q">
            Your question
          </label>
          <textarea
            id="q"
            className="input"
            rows={2}
            placeholder="Type your question…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                void send()
              }
            }}
            disabled={loading}
          />
          <button type="submit" className="send" disabled={loading || !input.trim()}>
            {loading ? 'Asking…' : 'Ask'}
          </button>
        </form>
        {error && <p className="err">{error}</p>}
      </main>
    </div>
  )
}
