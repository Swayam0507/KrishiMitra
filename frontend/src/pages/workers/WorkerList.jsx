import React, { useEffect, useState } from 'react'
import { Users, Plus, Phone, Award, Shield } from 'lucide-react'
import { workerService } from '../../services'
import { useToast } from '../../components/ui/Toast'

export default function WorkerList() {
  const { showToast } = useToast()
  const [workers, setWorkers] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadWorkers() {
      try {
        const res = await workerService.list().catch(() => ({ data: [] }))
        const list = res.data?.workers || res.data || [
          { id: '1', name: 'Ramesh Patel', role: 'Farm Supervisor', phone: '+91 98765 43210', skills: 'Irrigation, Crop Protection', status: 'Active' },
          { id: '2', name: 'Suresh Kumar', role: 'Field Technician', phone: '+91 98765 43211', skills: 'Spraying, Sensor Ops', status: 'Active' },
          { id: '3', name: 'Mahesh Shah', role: 'Agronomist Specialist', phone: '+91 98765 43212', skills: 'Soil Diagnostics, NPK', status: 'Active' },
          { id: '4', name: 'Dinesh Varma', role: 'General Laborer', phone: '+91 98765 43213', skills: 'Harvesting, Weeding', status: 'Active' }
        ]
        setWorkers(list)
      } catch (err) {
        showToast('Error loading workers', 'error')
      } finally {
        setLoading(false)
      }
    }
    loadWorkers()
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gradient">Farm Workforce</h1>
          <p className="text-sm text-muted">Manage field staff, supervisors, and task allocations</p>
        </div>
        <button onClick={() => showToast('Worker onboard form', 'info')} className="btn btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Add Worker
        </button>
      </div>

      {loading ? (
        <div className="card-glass p-6 text-center text-muted">Loading farm workforce...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {workers.map((w) => (
            <div key={w.id} className="card-glass p-5 flex flex-col justify-between hover:border-emerald-500/40 transition">
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-lg">
                    {w.name.charAt(0)}
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">{w.name}</h3>
                    <span className="text-xs text-emerald-300 font-medium">{w.role}</span>
                  </div>
                </div>
                <div className="text-xs space-y-1 text-muted">
                  <div className="flex items-center gap-1.5">
                    <Phone className="w-3.5 h-3.5 text-emerald-400" /> {w.phone}
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Award className="w-3.5 h-3.5 text-amber-400" /> {w.skills}
                  </div>
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-white/5 flex justify-between items-center">
                <span className="badge badge-success text-xs">{w.status}</span>
                <button className="text-xs text-muted hover:text-white">View Tasks</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
