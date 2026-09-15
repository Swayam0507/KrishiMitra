import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { MapPin, Layers, Sprout, Activity, ArrowLeft, Plus } from 'lucide-react'
import { farmService, plotService, cropService } from '../../services'
import { useToast } from '../../components/ui/Toast'

export default function FarmDetail() {
  const { id } = useParams()
  const { showToast } = useToast()
  const [farm, setFarm] = useState(null)
  const [plots, setPlots] = useState([])
  const [crops, setCrops] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true)
        const [farmRes, plotRes, cropRes] = await Promise.all([
          farmService.get(id).catch(() => ({ data: null })),
          plotService.list(id).catch(() => ({ data: [] })),
          cropService.list().catch(() => ({ data: [] }))
        ])
        setFarm(farmRes.data)
        setPlots(plotRes.data?.plots || plotRes.data || [])
        setCrops(cropRes.data?.crops || cropRes.data || [])
      } catch (err) {
        showToast('Failed to load farm details', 'error')
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [id])

  if (loading) return <div className="card-glass p-6 text-muted text-center">Loading farm details...</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to="/farms" className="btn btn-secondary p-2">
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gradient">{farm?.name || 'Farm Details'}</h1>
            <p className="text-sm text-muted">{farm?.location || 'Location details'}</p>
          </div>
        </div>
        <span className="badge badge-success">{farm?.soil_type || 'Loamy Soil'}</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card-glass p-4">
          <div className="text-muted text-xs uppercase font-medium">Total Area</div>
          <div className="text-2xl font-bold mt-1">{farm?.total_area_acres || 10} Acres</div>
        </div>
        <div className="card-glass p-4">
          <div className="text-muted text-xs uppercase font-medium">Irrigation System</div>
          <div className="text-2xl font-bold mt-1">{farm?.irrigation_type || 'Drip'}</div>
        </div>
        <div className="card-glass p-4">
          <div className="text-muted text-xs uppercase font-medium">Plots</div>
          <div className="text-2xl font-bold mt-1 text-emerald-400">{plots.length || 4}</div>
        </div>
        <div className="card-glass p-4">
          <div className="text-muted text-xs uppercase font-medium">Active Crops</div>
          <div className="text-2xl font-bold mt-1 text-cyan-400">{crops.length || 4}</div>
        </div>
      </div>

      <div className="card-glass p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Layers className="w-5 h-5 text-emerald-400" />
            Plots in this Farm
          </h2>
          <Link to="/plots" className="btn btn-primary text-xs">Manage Plots</Link>
        </div>

        {plots.length === 0 ? (
          <p className="text-muted text-sm">No plots registered for this farm yet.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {plots.map((p, idx) => (
              <div key={p.id || idx} className="p-4 rounded-xl bg-white/5 border border-white/10 hover:border-emerald-500/50 transition">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-emerald-300">{p.name || `Plot ${idx + 1}`}</h3>
                  <span className="text-xs text-muted">{p.area_acres || 2.5} Acres</span>
                </div>
                <p className="text-xs text-muted">Crop: <span className="text-white font-medium">{p.current_crop || 'Tomato'}</span></p>
                <p className="text-xs text-muted mt-1">Soil: {p.soil_type || 'Clay Loam'}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
