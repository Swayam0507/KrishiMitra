import React, { useState, useEffect } from 'react'
import { advisorService, farmService } from '../../services'
import { useToast } from '../../components/ui/Toast'
import { CheckCircle, Clock, XCircle, Play, ChevronDown } from 'lucide-react'

const STEPS = [
  { id: 'observe',        label: 'OBSERVE',        desc: 'Collecting farm data',          icon: '👁' },
  { id: 'analyze',        label: 'ANALYZE',        desc: 'Analyzing crop & soil state',   icon: '🔍' },
  { id: 'check_weather',  label: 'CHECK WEATHER',  desc: 'Fetching weather forecast',     icon: '🌤' },
  { id: 'check_telemetry',label: 'CHECK TELEMETRY',desc: 'Reading soil & crop metrics',   icon: '🌱' },
  { id: 'assess_risk',    label: 'ASSESS RISK',    desc: 'Computing disease & crop risk', icon: '⚠' },
  { id: 'decide',         label: 'DECIDE',         desc: 'Forming decision',              icon: '🧠' },
  { id: 'recommend',      label: 'RECOMMEND',      desc: 'Generating recommendation',     icon: '💡' },
  { id: 'monitor',        label: 'MONITOR',        desc: 'Scheduling next check',         icon: '📡' },
]

const STEP_STATUS = { pending: 'pending', running: 'running', done: 'done', error: 'error' }

export default function AgentAdvisor() {
  const toast = useToast()
  const [farms, setFarms] = useState([])
  const [selectedFarm, setSelectedFarm] = useState('')
  const [selectedCrop, setSelectedCrop] = useState('')
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])
  const [stepStatus, setStepStatus] = useState({})
  const [currentStepIdx, setCurrentStepIdx] = useState(-1)

  useEffect(() => {
    farmService.list().then(r => {
      setFarms(r.data || [])
      if (r.data?.length > 0) {
        setSelectedFarm(r.data[0].id)
        loadHistory(r.data[0].id)
      }
    }).catch(() => {})
  }, [])

  const loadHistory = (fid) => {
    advisorService.history(fid).then(r => setHistory(r.data || [])).catch(() => {})
  }

  const runAdvisor = async () => {
    if (!selectedFarm) { toast.error('Select a farm'); return }
    setRunning(true)
    setResult(null)
    setCurrentStepIdx(-1)
    setStepStatus(Object.fromEntries(STEPS.map(s => [s.id, STEP_STATUS.pending])))

    // Animate through steps
    for (let i = 0; i < STEPS.length; i++) {
      setCurrentStepIdx(i)
      setStepStatus(prev => ({ ...prev, [STEPS[i].id]: STEP_STATUS.running }))
      await new Promise(r => setTimeout(r, 600))
    }

    try {
      const res = await advisorService.run({
        farmId: selectedFarm,
        cropType: selectedCrop || undefined,
      })
      const data = res.data

      STEPS.forEach(s => {
        setStepStatus(prev => ({ ...prev, [s.id]: STEP_STATUS.done }))
      })

      setResult(data)
      toast.success('Advisor workflow complete!')
      loadHistory(selectedFarm)
    } catch (err) {
      toast.error('Advisor workflow failed')
      setStepStatus(prev => {
        const next = { ...prev }
        const pending = Object.keys(prev).find(k => prev[k] !== STEP_STATUS.done)
        if (pending) next[pending] = STEP_STATUS.error
        return next
      })
    } finally {
      setRunning(false)
      setCurrentStepIdx(-1)
    }
  }

  const stepIconForStatus = (status) => {
    if (status === 'done')    return <CheckCircle size={16} style={{ color: 'var(--accent-green)' }} />
    if (status === 'running') return <div className="loading-spinner" style={{ width: 16, height: 16 }} />
    if (status === 'error')   return <XCircle size={16} style={{ color: 'var(--accent-red)' }} />
    return <div style={{ width: 16, height: 16, borderRadius: '50%', background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)' }} />
  }

  const PRIORITY_COLOR = { High: 'var(--accent-red)', Medium: 'var(--accent-amber)', Low: 'var(--accent-green)', Critical: 'var(--accent-red)' }

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1>🤖 Agentic Farm Advisor</h1>
          <p>Deterministic AI advisory workflow — all actions are advisory only</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: 20 }}>
        {/* Left: Controls + Workflow Visualization */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="card">
            <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 14 }}>Run Advisor</h3>
            <div className="form-group mb-3">
              <label className="form-label">Farm</label>
              <select className="form-select" value={selectedFarm}
                onChange={e => { setSelectedFarm(e.target.value); loadHistory(e.target.value) }}>
                {farms.length === 0 && <option value="">No farms — add one first</option>}
                {farms.map(f => <option key={f.id} value={f.id}>{f.farmName}</option>)}
              </select>
            </div>
            <div className="form-group mb-4">
              <label className="form-label">Crop (optional)</label>
              <input className="form-input" placeholder="e.g. Tomato" value={selectedCrop}
                onChange={e => setSelectedCrop(e.target.value)} />
            </div>
            <button id="run-advisor-btn" className="btn btn-primary w-full" onClick={runAdvisor}
              disabled={running || !selectedFarm}>
              {running ? 'Running...' : <><Play size={15} /> Run Advisor Workflow</>}
            </button>
          </div>

          {/* Workflow Visualization */}
          <div className="card">
            <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 14, color: 'var(--text-secondary)' }}>WORKFLOW</h3>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              {STEPS.map((step, i) => (
                <React.Fragment key={step.id}>
                  <div className={`agent-step ${stepStatus[step.id] === 'done' ? 'completed' : stepStatus[step.id] === 'error' ? 'error' : ''}`}
                    style={{ background: stepStatus[step.id] === 'running' ? 'rgba(34,197,94,0.05)' : undefined }}>
                    <div className="agent-step-num" style={{ background: stepStatus[step.id] === 'running' ? 'rgba(34,197,94,0.2)' : undefined, color: stepStatus[step.id] === 'running' ? 'var(--accent-green)' : undefined }}>
                      {stepStatus[step.id] === 'pending' ? step.icon : stepIconForStatus(stepStatus[step.id])}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 12, fontWeight: 700, letterSpacing: '0.05em', color: stepStatus[step.id] === 'running' ? 'var(--accent-green)' : stepStatus[step.id] === 'done' ? 'var(--text-primary)' : 'var(--text-muted)' }}>
                        {step.label}
                      </div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{step.desc}</div>
                    </div>
                  </div>
                  {i < STEPS.length - 1 && (
                    <div style={{ display: 'flex', justifyContent: 'flex-start', paddingLeft: 20, color: 'var(--text-muted)' }}>
                      <ChevronDown size={14} />
                    </div>
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Result + History */}
        <div>
          {result ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {/* Main Decision */}
              <div className="card" style={{ borderTop: `3px solid ${PRIORITY_COLOR[result.priority] || 'var(--accent-green)'}` }}>
                <div className="flex items-center justify-between mb-3">
                  <span className="badge badge-green">ADVISOR DECISION</span>
                  <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{new Date().toLocaleString()}</span>
                </div>
                <h2 style={{ fontSize: 24, fontWeight: 800, fontFamily: 'Space Grotesk', marginBottom: 12 }}>
                  {result.decision}
                </h2>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                  {[
                    { label: 'Farm', value: result.farmContext?.farmName },
                    { label: 'Crop', value: result.farmContext?.cropType || 'General' },
                    { label: 'Soil Moisture', value: result.sensorContext?.soilMoisture ? `${result.sensorContext.soilMoisture.toFixed(1)}%` : 'N/A', note: 'SIMULATED' },
                    { label: 'Rain Probability', value: result.weatherContext?.rainProbability ? `${result.weatherContext.rainProbability}%` : 'N/A' },
                  ].map(f => (
                    <div key={f.label} style={{ background: 'var(--bg-secondary)', borderRadius: 8, padding: '10px 12px' }}>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        {f.label} {f.note && <span className="simulated-label">{f.note}</span>}
                      </div>
                      <div style={{ fontSize: 14, fontWeight: 600, marginTop: 2 }}>{f.value || '—'}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recommendations */}
              {result.recommendations?.length > 0 && (
                <div className="card">
                  <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 14 }}>💡 Recommendations</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {result.recommendations.map((r, i) => (
                      <div key={i} className="card" style={{ padding: '14px 16px', borderLeft: `3px solid ${PRIORITY_COLOR[r.priority] || 'var(--border-subtle)'}` }}>
                        <div className="flex items-center justify-between mb-2">
                          <div style={{ fontWeight: 600, fontSize: 14 }}>{r.title}</div>
                          <span className={`badge ${r.priority === 'High' || r.priority === 'Critical' ? 'badge-red' : r.priority === 'Medium' ? 'badge-amber' : 'badge-green'}`}>
                            {r.priority}
                          </span>
                        </div>
                        <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 6 }}>{r.reason}</div>
                        {r.recommendedAction && (
                          <div style={{ fontSize: 12, color: 'var(--accent-green)', fontWeight: 600 }}>
                            → {r.recommendedAction}
                          </div>
                        )}
                        {r.source && (
                          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>Source: {r.source}</div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {result.nextCheck && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 16px', background: 'rgba(34,197,94,0.08)', border: '1px solid rgba(34,197,94,0.2)', borderRadius: 10, fontSize: 13 }}>
                  <Clock size={16} style={{ color: 'var(--accent-green)' }} />
                  Next check scheduled: <strong>{result.nextCheck}</strong>
                </div>
              )}

              <div style={{ fontSize: 11, color: 'var(--text-muted)', textAlign: 'center', fontStyle: 'italic' }}>
                All advisor decisions are advisory. This is not an autonomous system. Decisions require human review.
              </div>
            </div>
          ) : (
            <div className="empty-state" style={{ minHeight: 400 }}>
              <div className="empty-state-icon">🤖</div>
              <h3>Run the Advisor Workflow</h3>
              <p>Select a farm and click "Run Advisor Workflow" to see the 8-step agentic decision process.</p>
            </div>
          )}

          {/* History */}
          {history.length > 0 && (
            <div className="card mt-4">
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 14 }}>Decision History</h3>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr><th>Decision</th><th>Priority</th><th>Date</th></tr>
                  </thead>
                  <tbody>
                    {history.slice(0, 10).map(h => (
                      <tr key={h.id}>
                        <td style={{ fontWeight: 600 }}>{h.decision}</td>
                        <td><span className={`badge ${h.priority === 'High' ? 'badge-red' : 'badge-amber'}`}>{h.priority}</span></td>
                        <td className="text-muted text-sm">{new Date(h.createdAt).toLocaleDateString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
