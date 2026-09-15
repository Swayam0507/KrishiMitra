import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Trash2, ChevronRight, MapPin, Layers } from 'lucide-react'
import { farmService } from '../../services'
import { useToast } from '../../components/ui/Toast'

const SOIL_COLORS = {
  Loamy: '#92400e', Clay: '#6b7280', Sandy: '#fbbf24',
  'Black Cotton': '#1f2937', 'Red Laterite': '#dc2626', Silty: '#7c3aed',
}

export default function FarmList() {
  const toast = useToast()
  const [farms, setFarms] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [form, setForm] = useState({
    farmName: '', location: '', area: '', areaUnit: 'acres',
    soilType: 'Loamy', irrigationType: 'Drip', latitude: '', longitude: '',
  })

  useEffect(() => { load() }, [])

  const load = async () => {
    setLoading(true)
    try {
      const res = await farmService.list()
      setFarms(res.data)
    } catch { toast.error('Failed to load farms') }
    finally { setLoading(false) }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.farmName || !form.location || !form.area) { toast.error('Fill required fields'); return }
    setSubmitting(true)
    try {
      const payload = { ...form, area: parseFloat(form.area), latitude: form.latitude ? parseFloat(form.latitude) : undefined, longitude: form.longitude ? parseFloat(form.longitude) : undefined }
      await farmService.create(payload)
      toast.success('Farm created!')
      setShowForm(false)
      setForm({ farmName: '', location: '', area: '', areaUnit: 'acres', soilType: 'Loamy', irrigationType: 'Drip', latitude: '', longitude: '' })
      load()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create farm')
    } finally { setSubmitting(false) }
  }

  const handleDelete = async (id, name) => {
    if (!confirm(`Delete "${name}"? This cannot be undone.`)) return
    try {
      await farmService.delete(id)
      toast.success('Farm deleted')
      setFarms(p => p.filter(f => f.id !== id))
    } catch { toast.error('Failed to delete') }
  }

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1>My Farms</h1>
          <p>Manage your agricultural farms and fields</p>
        </div>
        <div className="page-header-actions">
          <button id="add-farm-btn" className="btn btn-primary" onClick={() => setShowForm(true)}>
            <Plus size={16} /> Add Farm
          </button>
        </div>
      </div>

      {/* Add Farm Form */}
      {showForm && (
        <div className="card mb-4">
          <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 20 }}>New Farm</h3>
          <form onSubmit={handleSubmit}>
            <div className="grid-2 gap-3">
              <div className="form-group">
                <label className="form-label">Farm Name *</label>
                <input className="form-input" placeholder="e.g. Patel's North Farm" value={form.farmName}
                  onChange={e => setForm(p => ({ ...p, farmName: e.target.value }))} required />
              </div>
              <div className="form-group">
                <label className="form-label">Location *</label>
                <input className="form-input" placeholder="e.g. Anand, Gujarat" value={form.location}
                  onChange={e => setForm(p => ({ ...p, location: e.target.value }))} required />
              </div>
              <div className="form-group">
                <label className="form-label">Area *</label>
                <div className="flex gap-2">
                  <input className="form-input" type="number" min="0" placeholder="10" value={form.area}
                    onChange={e => setForm(p => ({ ...p, area: e.target.value }))} required style={{ flex: 1 }} />
                  <select className="form-select" value={form.areaUnit}
                    onChange={e => setForm(p => ({ ...p, areaUnit: e.target.value }))} style={{ width: 120 }}>
                    <option value="acres">Acres</option>
                    <option value="hectares">Hectares</option>
                    <option value="bigha">Bigha</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Soil Type</label>
                <select className="form-select" value={form.soilType}
                  onChange={e => setForm(p => ({ ...p, soilType: e.target.value }))}>
                  {['Loamy','Clay','Sandy','Silty','Peaty','Chalky','Black Cotton','Red Laterite'].map(s => <option key={s}>{s}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Irrigation Type</label>
                <select className="form-select" value={form.irrigationType}
                  onChange={e => setForm(p => ({ ...p, irrigationType: e.target.value }))}>
                  {['Drip','Sprinkler','Flood','Furrow','Canal','Rain-fed','Borewell'].map(s => <option key={s}>{s}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Coordinates (optional)</label>
                <div className="flex gap-2">
                  <input className="form-input" type="number" step="any" placeholder="Latitude" value={form.latitude}
                    onChange={e => setForm(p => ({ ...p, latitude: e.target.value }))} />
                  <input className="form-input" type="number" step="any" placeholder="Longitude" value={form.longitude}
                    onChange={e => setForm(p => ({ ...p, longitude: e.target.value }))} />
                </div>
              </div>
            </div>
            <div className="flex gap-3 mt-4">
              <button type="submit" className="btn btn-primary" disabled={submitting}>
                {submitting ? 'Creating...' : 'Create Farm'}
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      {/* Farm Grid */}
      {loading ? (
        <div className="grid-3">{[1,2,3].map(i => <div key={i} className="skeleton-card"><div className="skeleton" style={{ height: 120 }} /></div>)}</div>
      ) : farms.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🌾</div>
          <h3>No farms yet</h3>
          <p>Create your first farm to start using AgriFlow AI</p>
          <button className="btn btn-primary mt-3" onClick={() => setShowForm(true)}>
            <Plus size={16} /> Add Your First Farm
          </button>
        </div>
      ) : (
        <div className="grid-3">
          {farms.map(farm => (
            <div key={farm.id} className="card" style={{ position: 'relative' }}>
              <div className="flex items-center justify-between mb-3">
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{ width: 40, height: 40, borderRadius: 10, background: `${SOIL_COLORS[farm.soilType] || '#16a34a'}33`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20 }}>
                    🌾
                  </div>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: 15 }}>{farm.farmName}</div>
                    <div className="flex items-center gap-1 text-muted text-xs">
                      <MapPin size={11} />{farm.location}
                    </div>
                  </div>
                </div>
                <button onClick={() => handleDelete(farm.id, farm.farmName)}
                  className="btn btn-ghost btn-icon" style={{ color: 'var(--text-muted)' }}>
                  <Trash2 size={14} />
                </button>
              </div>

              <div className="grid-2" style={{ gap: 8, marginBottom: 14 }}>
                {[
                  { label: 'Area', value: `${farm.area} ${farm.areaUnit}` },
                  { label: 'Soil', value: farm.soilType },
                  { label: 'Irrigation', value: farm.irrigationType },
                  { label: 'ID', value: farm.id.substring(0, 8) + '...', mono: true },
                ].map(f => (
                  <div key={f.label} style={{ background: 'var(--bg-secondary)', borderRadius: 8, padding: '8px 10px' }}>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{f.label}</div>
                    <div style={{ fontSize: 13, fontWeight: 600, marginTop: 2, fontFamily: f.mono ? 'monospace' : undefined }}>{f.value}</div>
                  </div>
                ))}
              </div>

              <div className="flex gap-2">
                <Link to={`/farms/${farm.id}`} className="btn btn-primary btn-sm" style={{ flex: 1, justifyContent: 'center' }}>
                  View <ChevronRight size={13} />
                </Link>
                <Link to={`/plots?farmId=${farm.id}`} className="btn btn-secondary btn-sm" style={{ flex: 1, justifyContent: 'center' }}>
                  <Layers size={13} /> Plots
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
