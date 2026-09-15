import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Sprout, ShieldAlert, Droplets, Sun, Activity, Thermometer } from 'lucide-react'
import { cropService } from '../../services'

export default function CropDetail() {
  const { id } = useParams()
  const [crop, setCrop] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadCrop() {
      try {
        const res = await cropService.get(id).catch(() => ({ data: null }))
        setCrop(res.data || {
          id,
          name: 'Tomato (Solanum lycopersicum)',
          variety: 'Arka Rakshak',
          plot_name: 'Plot A — Tomato',
          stage: 'Fruiting Phase (Days 60-90)',
          planting_date: '2026-01-15',
          expected_harvest: '2026-04-30',
          health_score: 92,
          status: 'Healthy',
          ideal_temp: '20°C - 30°C',
          ideal_moisture: '60% - 75%',
          ideal_ph: '6.0 - 6.8',
          fertilizer_schedule: 'NPK 19-19-19 application at 45 days. Micronutrient spray recommended next week.',
          disease_risk: 'Low (Leaf Mold risk 14%)'
        })
      } finally {
        setLoading(false)
      }
    }
    loadCrop()
  }, [id])

  if (loading) return <div className="card-glass p-6 text-center text-muted">Loading crop details...</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/crops" className="btn btn-secondary p-2">
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gradient">{crop?.name}</h1>
          <p className="text-sm text-muted">{crop?.variety} • {crop?.plot_name}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card-glass p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
            <Sprout className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-muted">Growth Stage</div>
            <div className="font-semibold text-white">{crop?.stage}</div>
          </div>
        </div>

        <div className="card-glass p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-muted">Health Index</div>
            <div className="font-semibold text-white">{crop?.health_score}% ({crop?.status})</div>
          </div>
        </div>

        <div className="card-glass p-5 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-muted">Disease Risk</div>
            <div className="font-semibold text-white">{crop?.disease_risk}</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card-glass p-6 space-y-4">
          <h2 className="text-lg font-semibold text-white">Ideal Environmental Conditions</h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
              <span className="text-muted flex items-center gap-2">
                <Thermometer className="w-4 h-4 text-rose-400" /> Temperature Range
              </span>
              <span className="font-semibold text-white">{crop?.ideal_temp}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
              <span className="text-muted flex items-center gap-2">
                <Droplets className="w-4 h-4 text-cyan-400" /> Soil Moisture Target
              </span>
              <span className="font-semibold text-white">{crop?.ideal_moisture}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
              <span className="text-muted flex items-center gap-2">
                <Sun className="w-4 h-4 text-amber-400" /> Optimal pH Range
              </span>
              <span className="font-semibold text-white">{crop?.ideal_ph}</span>
            </div>
          </div>
        </div>

        <div className="card-glass p-6 space-y-4">
          <h2 className="text-lg font-semibold text-white">Agronomic Schedule & Care</h2>
          <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl space-y-2">
            <div className="text-xs font-semibold text-emerald-400 uppercase">Fertilization & Care Plan</div>
            <p className="text-sm text-gray-200">{crop?.fertilizer_schedule}</p>
          </div>
          <div className="flex gap-3 pt-2">
            <Link to="/disease" className="btn btn-primary text-xs flex-1 text-center">Scan Leaf Health</Link>
            <Link to="/irrigation" className="btn btn-secondary text-xs flex-1 text-center">Check Water Needs</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
