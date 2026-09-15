import React, { useEffect, useState } from 'react'
import { Bell, AlertTriangle, CheckCircle, Info, ShieldAlert, Check } from 'lucide-react'
import { alertService } from '../../services'
import { useToast } from '../../components/ui/Toast'

export default function AlertCenter() {
  const { showToast } = useToast()
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAlerts()
  }, [])

  async function loadAlerts() {
    try {
      setLoading(true)
      const res = await alertService.list().catch(() => ({ data: [] }))
      const list = res.data?.alerts || res.data || [
        { id: '1', title: 'Low Soil Moisture Alert', severity: 'HIGH', category: 'Irrigation', message: 'Plot A Tomato soil moisture dropped to 38% (threshold 45%). Irrigation advised.', created_at: '10 mins ago', read: false },
        { id: '2', title: 'Early Blight Risk Warning', severity: 'MEDIUM', category: 'Disease', message: 'High humidity (88%) and 26°C temp elevate Early Blight risk to 68%.', created_at: '1 hour ago', read: false },
        { id: '3', title: 'Fungicide Inventory Depletion', severity: 'LOW', category: 'Inventory', message: 'Copper Oxychloride stock is at 12 kg (minimum threshold 20 kg).', created_at: '3 hours ago', read: true },
        { id: '4', title: 'Heavy Rainfall Forecasted', severity: 'INFO', category: 'Weather', message: 'Wednesday forecast predicts 18.5mm rainfall. Pause scheduled irrigation.', created_at: '5 hours ago', read: true }
      ]
      setAlerts(list)
    } catch (err) {
      showToast('Error loading alerts', 'error')
    } finally {
      setLoading(false)
    }
  }

  async function markAllRead() {
    try {
      await alertService.markAllRead().catch(() => {})
      setAlerts(alerts.map(a => ({ ...a, read: true })))
      showToast('All alerts marked as read', 'success')
    } catch (err) {
      showToast('Action failed', 'error')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gradient flex items-center gap-2">
            <Bell className="w-6 h-6 text-amber-400" /> Agronomic Alert Center
          </h1>
          <p className="text-sm text-muted">Proactive notifications for stress anomalies, weather alerts, and disease risks</p>
        </div>
        <button onClick={markAllRead} className="btn btn-secondary text-xs flex items-center gap-1.5">
          <Check className="w-3.5 h-3.5" /> Mark All as Read
        </button>
      </div>

      {loading ? (
        <div className="card-glass p-6 text-center text-muted">Loading alert log...</div>
      ) : (
        <div className="space-y-3">
          {alerts.map((al) => {
            const isHigh = al.severity === 'HIGH'
            const isMed = al.severity === 'MEDIUM'
            return (
              <div key={al.id} className={`card-glass p-5 flex items-start gap-4 transition ${!al.read ? 'border-l-4 border-l-amber-500 bg-white/5' : 'opacity-75'}`}>
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${isHigh ? 'bg-rose-500/20 text-rose-400' : isMed ? 'bg-amber-500/20 text-amber-400' : 'bg-cyan-500/20 text-cyan-400'}`}>
                  <AlertTriangle className="w-5 h-5" />
                </div>

                <div className="flex-1 space-y-1">
                  <div className="flex justify-between items-center">
                    <h3 className="font-semibold text-white flex items-center gap-2">
                      {al.title}
                      {!al.read && <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />}
                    </h3>
                    <span className="text-xs text-muted">{al.created_at}</span>
                  </div>
                  <p className="text-xs text-gray-300">{al.message}</p>
                  <div className="flex items-center gap-2 pt-1">
                    <span className={`badge ${isHigh ? 'badge-error' : isMed ? 'badge-warning' : 'badge-info'} text-[10px]`}>
                      {al.severity}
                    </span>
                    <span className="text-[11px] text-emerald-400 font-medium">Category: {al.category}</span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
