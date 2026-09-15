import React, { useState, useEffect, useRef } from 'react'
import { Bot, Send, Mic, MicOff, Info, Loader2 } from 'lucide-react'
import { assistantService, farmService } from '../../services'
import { useToast } from '../../components/ui/Toast'
import { useLanguage } from '../../context/LanguageContext'

const QUICK_QUESTIONS = [
  'What is the health status of my farm?',
  'Should I irrigate my crops today?',
  'What disease risk is there for my crops?',
  'What fertilizer should I use this week?',
  'Is today a good day for spraying?',
  'Explain the sustainability score of my farm.',
]

export default function Assistant() {
  const toast = useToast()
  const { lang } = useLanguage()
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '🌾 Hello! I\'m the AgriFlow AI Assistant. I\'m grounded in your real farm data — I can answer questions about your crops, disease risk, weather, sensor readings, irrigation recommendations, and sustainability.\n\nI use real application data and will clearly tell you when information is not available. What would you like to know?',
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId] = useState(() => `sess-${Date.now()}`)
  const [farms, setFarms] = useState([])
  const [selectedFarm, setSelectedFarm] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [voiceSupported, setVoiceSupported] = useState(false)
  const [isDemoMode, setIsDemoMode] = useState(false)
  const messagesEndRef = useRef(null)
  const recognitionRef = useRef(null)

  useEffect(() => {
    farmService.list().then(r => {
      setFarms(r.data || [])
      if (r.data?.length > 0) setSelectedFarm(r.data[0].id)
    }).catch(() => {})

    // Check voice support
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
      setVoiceSupported(true)
    }
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (text) => {
    const msg = text || input.trim()
    if (!msg) return
    setInput('')

    const userMsg = { role: 'user', content: msg }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)

    try {
      const res = await assistantService.chat({
        message: msg,
        sessionId,
        farmId: selectedFarm || undefined,
        language: lang,
      })
      const data = res.data
      setIsDemoMode(data.mode === 'demo')
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response,
        mode: data.mode,
      }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '⚠ I encountered an error. Please try again.',
        error: true,
      }])
      toast.error('Assistant error')
    } finally {
      setLoading(false)
    }
  }

  const startVoice = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) { toast.error('Voice not supported in this browser'); return }

    const rec = new SR()
    recognitionRef.current = rec
    const langMap = { en: 'en-IN', hi: 'hi-IN', gu: 'gu-IN' }
    rec.lang = langMap[lang] || 'en-IN'
    rec.interimResults = false

    rec.onresult = (e) => {
      const transcript = e.results[0][0].transcript
      setInput(transcript)
    }
    rec.onerror = () => { toast.error('Voice recognition failed'); setIsListening(false) }
    rec.onend  = () => setIsListening(false)

    rec.start()
    setIsListening(true)
  }

  const stopVoice = () => {
    recognitionRef.current?.stop()
    setIsListening(false)
  }

  const speak = (text) => {
    if (!window.speechSynthesis) return
    window.speechSynthesis.cancel()
    const utt = new SpeechSynthesisUtterance(text)
    const langMap = { en: 'en-IN', hi: 'hi-IN', gu: 'gu-IN' }
    utt.lang = langMap[lang] || 'en-IN'
    utt.rate = 0.9
    window.speechSynthesis.speak(utt)
  }

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1>💬 AI Farm Assistant</h1>
          <p>Grounded agricultural assistant powered by real farm data</p>
        </div>
        <div className="page-header-actions">
          {farms.length > 0 && (
            <select className="form-select" value={selectedFarm} onChange={e => setSelectedFarm(e.target.value)} style={{ width: 200 }}>
              <option value="">No farm selected</option>
              {farms.map(f => <option key={f.id} value={f.id}>{f.farmName}</option>)}
            </select>
          )}
          {isDemoMode && <span className="demo-banner">📋 DEMO ASSISTANT</span>}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: 20, height: 'calc(100vh - 200px)' }}>
        {/* Chat */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}>
          {/* Messages */}
          <div className="chat-messages" style={{ flex: 1, overflowY: 'auto' }}>
            {messages.map((m, i) => (
              <div key={i} className={`chat-bubble ${m.role}`}>
                {m.role === 'assistant' && (
                  <div className="flex items-center gap-2 mb-2">
                    <div style={{ width: 22, height: 22, background: 'var(--accent-green-dim)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12 }}>🌾</div>
                    <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--accent-green)' }}>AgriFlow AI</span>
                    {m.mode === 'demo' && <span className="simulated-label">DEMO</span>}
                    {m.mode === 'gemini' && <span className="badge badge-purple" style={{ fontSize: 9 }}>GEMINI</span>}
                  </div>
                )}
                <div style={{ whiteSpace: 'pre-wrap', fontSize: 14 }}>{m.content}</div>
                {m.role === 'assistant' && !m.error && (
                  <button
                    onClick={() => speak(m.content)}
                    style={{ marginTop: 8, background: 'none', border: 'none', cursor: 'pointer', fontSize: 11, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}
                  >
                    🔊 Listen
                  </button>
                )}
              </div>
            ))}
            {loading && (
              <div className="chat-bubble assistant" style={{ opacity: 0.6 }}>
                <div className="flex items-center gap-2">
                  <div className="loading-spinner" style={{ width: 14, height: 14 }} />
                  <span style={{ fontSize: 13 }}>Thinking...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="chat-input-bar">
            {voiceSupported && (
              <button
                onClick={isListening ? stopVoice : startVoice}
                className={`btn ${isListening ? 'btn-danger' : 'btn-secondary'} btn-icon`}
                title={isListening ? 'Stop listening' : 'Voice input'}
              >
                {isListening ? <MicOff size={16} /> : <Mic size={16} />}
              </button>
            )}
            <textarea
              className="form-input"
              placeholder="Ask anything about your farm..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() } }}
              rows={1}
              style={{ flex: 1, resize: 'none', minHeight: 40 }}
            />
            <button
              id="assistant-send"
              className="btn btn-primary btn-icon"
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
            >
              <Send size={16} />
            </button>
          </div>
        </div>

        {/* Sidebar */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="card">
            <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 12, color: 'var(--text-secondary)' }}>QUICK QUESTIONS</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {QUICK_QUESTIONS.map(q => (
                <button
                  key={q}
                  className="btn btn-ghost btn-sm"
                  style={{ justifyContent: 'flex-start', textAlign: 'left', whiteSpace: 'normal', height: 'auto', padding: '8px 12px', lineHeight: 1.4 }}
                  onClick={() => sendMessage(q)}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 10, color: 'var(--text-secondary)' }}>DATA SOURCES</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 12 }}>
              {[
                { icon: '🌾', label: 'Farm & Crop data', status: 'Live' },
                { icon: '🔬', label: 'Disease history', status: 'Live' },
                { icon: '🌤', label: 'Weather data', status: 'Live' },
                { icon: '⚡', label: 'Sensor readings', status: 'Simulated' },
                { icon: '💧', label: 'Irrigation advice', status: 'Live' },
                { icon: '🌱', label: 'Sustainability', status: 'Live' },
              ].map(d => (
                <div key={d.label} className="flex items-center justify-between">
                  <span>{d.icon} {d.label}</span>
                  <span className={`badge ${d.status === 'Live' ? 'badge-green' : 'badge-amber'}`} style={{ fontSize: 9 }}>{d.status}</span>
                </div>
              ))}
            </div>
          </div>

          <div style={{ padding: '10px 12px', background: 'rgba(59,130,246,0.08)', border: '1px solid rgba(59,130,246,0.15)', borderRadius: 8, fontSize: 11, color: 'var(--accent-blue)' }}>
            <Info size={12} style={{ display: 'inline', marginRight: 4, verticalAlign: 'middle' }} />
            This assistant uses real farm data. It does not invent sensor readings, weather, or disease results. If Gemini API is unavailable, Demo mode is used.
          </div>
        </div>
      </div>
    </div>
  )
}
