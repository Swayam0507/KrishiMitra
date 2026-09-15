import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Layers, Plus, Map, Sprout, Trash2 } from 'lucide-react'
import { plotService, farmService } from '../../services'
import { useToast } from '../../components/ui/Toast'

export default function PlotList() {
  const { showToast } = useToast()
  const [plots, setPlots] = useState([])
  const [farms, setFarms] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAddModal, setShowAddModal] = useState(false)
  const [formData, setFormData] = useState({ name: '', farm_id: '', area_acres: 2.5, soil_type: 'Loam' })

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    try {
      setLoading(true)
      const [plotRes, farmRes] = await Promise.all([
        plotService.list().catch(() => ({ data: [] })),
        farmService.list().catch(() => ({ data: [] }))
      ])
      const fetchedPlots = plotRes.data?.plots || plotRes.data || [
        { id: '1', name: 'Plot A — Main North', farm_name: 'AgriFlow Demo Farm', area_acres: 2.5, soil_type: 'Clay Loam', current_crop: 'Tomato' },
        { id: '2', name: 'Plot B — South Field', farm_name: 'AgriFlow Demo Farm', area_acres: 2.5, soil_type: 'Sandy Loam', current_crop: 'Potato' },
        { id: '3', name: 'Plot C — East Ridge', farm_name: 'AgriFlow Demo Farm', area_acres: 2.5, soil_type: 'Black Cotton', current_crop: 'Corn' },
        { id: '4', name: 'Plot D — West Terrace', farm_name: 'AgriFlow Demo Farm', area_acres: 2.5, soil_type: 'Red Loam', current_crop: 'Pepper' }
      ]
      const fetchedFarms = farmRes.data?.farms || farmRes.data || []
      setPlots(fetchedPlots)
      setFarms(fetchedFarms)
    } catch (err) {
      showToast('Error loading plots', 'error')
    } finally {
      setLoading(false)
    }
  }

  async function handleSubmit(e) {
    e.preventDefault()
    try {
      await plotService.create(formData)
      showToast('Plot created successfully', 'success')
      setShowAddModal(false)
      loadData()
    } catch (err) {
      showToast('Failed to create plot', 'error')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gradient">Farm Plots</h1>
          <p className="text-sm text-muted">Manage land parcels and soil profiles across farms</p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="btn btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Add Plot
        </button>
      </div>

      {loading ? (
        <div className="card-glass p-6 text-center text-muted">Loading plots...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {plots.map((plot) => (
            <div key={plot.id} className="card-glass p-5 flex flex-col justify-between hover:border-emerald-500/40 transition">
              <div>
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-lg text-white">{plot.name}</h3>
                  <span className="badge badge-info">{plot.area_acres} Acres</span>
                </div>
                <p className="text-xs text-muted flex items-center gap-1 mb-3">
                  <Map className="w-3.5 h-3.5 text-emerald-400" />
                  {plot.farm_name || 'AgriFlow Demo Farm'}
                </p>
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between text-muted">
                    <span>Soil Type:</span>
                    <span className="text-white font-medium">{plot.soil_type}</span>
                  </div>
                  <div className="flex justify-between text-muted">
                    <span>Current Crop:</span>
                    <span className="text-emerald-400 font-medium">{plot.current_crop || 'Active'}</span>
                  </div>
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-white/5 flex justify-between items-center text-xs">
                <Link to={`/crops`} className="text-emerald-400 hover:underline flex items-center gap-1">
                  <Sprout className="w-3.5 h-3.5" /> View Crops
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      {showAddModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="card-glass p-6 w-full max-w-md space-y-4">
            <h2 className="text-lg font-bold text-white">Add New Plot</h2>
            <form onSubmit={handleSubmit} className="space-y-3">
              <div>
                <label className="text-xs text-muted block mb-1">Plot Name</label>
                <input required type="text" className="input-field" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} placeholder="e.g. Plot E - Greenhouse" />
              </div>
              <div>
                <label className="text-xs text-muted block mb-1">Area (Acres)</label>
                <input required type="number" step="0.1" className="input-field" value={formData.area_acres} onChange={e => setFormData({...formData, area_acres: parseFloat(e.target.value)})} />
              </div>
              <div>
                <label className="text-xs text-muted block mb-1">Soil Type</label>
                <select className="input-field" value={formData.soil_type} onChange={e => setFormData({...formData, soil_type: e.target.value})}>
                  <option value="Loam">Loam</option>
                  <option value="Clay Loam">Clay Loam</option>
                  <option value="Sandy Loam">Sandy Loam</option>
                  <option value="Black Cotton">Black Cotton</option>
                  <option value="Red Soil">Red Soil</option>
                </select>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setShowAddModal(false)} className="btn btn-secondary">Cancel</button>
                <button type="submit" className="btn btn-primary">Save Plot</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
