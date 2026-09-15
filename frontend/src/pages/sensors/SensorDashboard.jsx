import React, { useEffect, useState } from 'react'
import { Activity, Play, Square, RefreshCw, Thermometer, Droplets, Sun, Zap } from 'lucide-react'
import { sensorService, anomalyService } from '../../services'
import { useToast } from '../../components/ui/Toast'

export default function SensorDashboard() {
  const { showToast } = useToast()
  const [readings, setReadings] = useState([])
  const [simulating, setSimulating] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadReadings()
  }, [])

  async function loadReadings() {
    try {
      setLoading(true)
      const res = await sensorService.readings().catch(() => ({ data: [] }))
      const list = res.data?.readings || res.data || [
        { timestamp: '11:50 AM', plot: 'Plot A — Tomato', temperature: 28.4, soil_moisture: 42.1, ph: 6.4, npk: 'N:90 P:42 K:43' },
        { timestamp: '11:45 AM', plot: 'Plot B — Potato', temperature: 27.9, soil_moisture: 38.5, ph: 6.2, npk: 'N:85 P:40 K:45' },
        { timestamp: '11:40 AM', plot: 'Plot C — Corn', temperature: 29.1, soil_moisture: 51.0, ph: 6.8, npk: 'N:110 P:55 K:50' },
        { timestamp: '11:35 AM', plot: 'Plot D — Pepper', temperature: 28.8, soil_moisture: 44.2, ph: 6.5, npk: 'N:78 P:38 K:40' }
      ]
      setReadings(list)
    } catch (err) {
      showToast('Error loading telemetry', 'error')
    } finally {
      setLoading(false)
    }
  }

  async function toggleSimulation() {
    try {
      if (simulating) {
        await sensorService.stop().catch(() => {})
        setSimulating(false)
        showToast('IoT Telemetry Stream Stopped', 'info')
      } else {
        await sensorService.start('farm-1', 5).catch(() => {})
        setSimulating(true)
        showToast('IoT Sensor Simulator Active (5s ticker)', 'success')
      }
    } catch (err) {
      showToast('Simulation state change failed', 'error')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gradient flex items-center gap-2">
            <Activity className="w-6 h-6 text-emerald-400" /> Real-time IoT Sensor Mesh
          </h1>
          <p className="text-sm text-muted">Telemetry stream for soil moisture, temperature, pH, and NPK nodes</p>
        </div>
        <div className="flex gap-2">
          <button onClick={loadReadings} className="btn btn-secondary p-2.5">
            <RefreshCw className="w-4 h-4" />
          </button>
          <button onClick={toggleSimulation} className={`btn ${simulating ? 'btn-danger' : 'btn-primary'} flex items-center gap-2`}>
            {simulating ? <Square className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            {simulating ? 'Stop Stream' : 'Start IoT Simulation'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card-glass p-4 border-l-4 border-l-emerald-500">
          <div className="text-muted text-xs uppercase font-medium">Active Sensor Nodes</div>
          <div className="text-2xl font-bold text-white mt-1">16 Nodes (Online)</div>
        </div>
        <div className="card-glass p-4 border-l-4 border-l-cyan-500">
          <div className="text-muted text-xs uppercase font-medium">Average Soil Moisture</div>
          <div className="text-2xl font-bold text-cyan-400 mt-1">43.9%</div>
        </div>
        <div className="card-glass p-4 border-l-4 border-l-amber-500">
          <div className="text-muted text-xs uppercase font-medium">Mean Ambient Temp</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">28.5°C</div>
        </div>
        <div className="card-glass p-4 border-l-4 border-l-purple-500">
          <div className="text-muted text-xs uppercase font-medium">Telemetry Rate</div>
          <div className="text-2xl font-bold text-purple-400 mt-1">1 msg / 5s</div>
        </div>
      </div>

      {loading ? (
        <div className="card-glass p-6 text-center text-muted">Loading telemetry stream...</div>
      ) : (
        <div className="card-glass overflow-hidden">
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="border-b border-white/10 bg-white/5 text-muted text-xs uppercase font-semibold">
                <th className="p-4">Timestamp</th>
                <th className="p-4">Plot Node</th>
                <th className="p-4">Soil Moisture</th>
                <th className="p-4">Temperature</th>
                <th className="p-4">pH Level</th>
                <th className="p-4">Nutrient Ratio (NPK)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 font-mono text-xs">
              {readings.map((r, i) => (
                <tr key={i} className="hover:bg-white/5 transition">
                  <td className="p-4 text-muted">{r.timestamp}</td>
                  <td className="p-4 font-sans font-semibold text-white">{r.plot}</td>
                  <td className="p-4 text-cyan-400 font-bold">{r.soil_moisture}%</td>
                  <td className="p-4 text-amber-400">{r.temperature}°C</td>
                  <td className="p-4 text-purple-300">{r.ph}</td>
                  <td className="p-4 text-emerald-400">{r.npk}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
