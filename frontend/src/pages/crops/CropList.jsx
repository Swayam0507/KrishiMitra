import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Sprout, Plus, Calendar, Activity, Eye } from 'lucide-react'
import { cropService } from '../../services'
import { useToast } from '../../components/ui/Toast'

export default function CropList() {
  const { showToast } = useToast()
  const [crops, setCrops] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadCrops() {
      try {
        const res = await cropService.list().catch(() => ({ data: [] }))
        const fetchedCrops = res.data?.crops || res.data || [
          { id: '1', name: 'Tomato (Solanum lycopersicum)', variety: 'Arka Rakshak', plot_name: 'Plot A — Tomato', stage: 'Fruiting', planting_date: '2026-01-15', health_score: 92, status: 'Active' },
          { id: '2', name: 'Potato (Solanum tuberosum)', variety: 'Kufri Pukhraj', plot_name: 'Plot B — Potato', stage: 'Tuber Initiation', planting_date: '2026-02-01', health_score: 88, status: 'Active' },
          { id: '3', name: 'Corn (Zea mays)', variety: 'Hybrid Sweet Corn', plot_name: 'Plot C — Corn', stage: 'Vegetative', planting_date: '2026-02-10', health_score: 95, status: 'Active' },
          { id: '4', name: 'Bell Pepper (Capsicum annuum)', variety: 'Indam 984', plot_name: 'Plot D — Pepper', stage: 'Flowering', planting_date: '2026-01-20', health_score: 84, status: 'Active' }
        ]
        setCrops(fetchedCrops)
      } catch (err) {
        showToast('Error loading crops', 'error')
      } finally {
        setLoading(false)
      }
    }
    loadCrops()
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gradient">Active Crops</h1>
          <p className="text-sm text-muted">Monitor crop lifecycle, health stages, and growth tracking</p>
        </div>
        <Link to="/recommendation" className="btn btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Recommend New Crop
        </Link>
      </div>

      {loading ? (
        <div className="card-glass p-6 text-center text-muted">Loading active crops...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4">
          {crops.map((crop) => (
            <div key={crop.id} className="card-glass p-5 space-y-4 border border-white/10 hover:border-emerald-500/40 transition">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-bold text-lg text-white flex items-center gap-2">
                    <Sprout className="w-5 h-5 text-emerald-400" />
                    {crop.name}
                  </h3>
                  <p className="text-xs text-muted">Variety: <span className="text-emerald-300">{crop.variety}</span> • {crop.plot_name}</p>
                </div>
                <span className={`badge ${crop.health_score > 90 ? 'badge-success' : 'badge-warning'}`}>
                  Score: {crop.health_score}%
                </span>
              </div>

              <div className="grid grid-cols-3 gap-2 py-2 bg-white/5 rounded-lg text-center text-xs">
                <div>
                  <div className="text-muted">Growth Stage</div>
                  <div className="font-semibold text-white mt-0.5">{crop.stage}</div>
                </div>
                <div>
                  <div className="text-muted">Planting Date</div>
                  <div className="font-semibold text-white mt-0.5">{crop.planting_date}</div>
                </div>
                <div>
                  <div className="text-muted">Status</div>
                  <div className="font-semibold text-emerald-400 mt-0.5">{crop.status}</div>
                </div>
              </div>

              <div className="flex justify-between items-center pt-2">
                <Link to={`/crops/${crop.id}`} className="btn btn-secondary text-xs flex items-center gap-1.5">
                  <Eye className="w-3.5 h-3.5" /> Crop Details
                </Link>
                <Link to="/disease" className="text-xs text-emerald-400 hover:underline">
                  Run Disease Diagnostic →
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
