import React, { useEffect, useState } from 'react'
import { ClipboardList, Plus, CheckCircle, Clock, Calendar } from 'lucide-react'
import { activityService } from '../../services'
import { useToast } from '../../components/ui/Toast'

export default function ActivityList() {
  const { showToast } = useToast()
  const [activities, setActivities] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadActivities() {
      try {
        const res = await activityService.list().catch(() => ({ data: [] }))
        const list = res.data?.activities || res.data || [
          { id: '1', title: 'Drip Irrigation Cycle #42', category: 'Irrigation', plot: 'Plot A — Tomato', date: '2026-09-13', status: 'Completed', assigned_to: 'Ramesh Patel' },
          { id: '2', title: 'Fungicide Spraying (Copper Oxychloride)', category: 'Pest Control', plot: 'Plot B — Potato', date: '2026-09-13', status: 'In Progress', assigned_to: 'Suresh Kumar' },
          { id: '3', title: 'Soil NPK & Moisture Sampling', category: 'Maintenance', plot: 'Plot C — Corn', date: '2026-09-14', status: 'Scheduled', assigned_to: 'Mahesh Shah' },
          { id: '4', title: 'Weeding & Mulching Inspection', category: 'Cultivation', plot: 'Plot D — Pepper', date: '2026-09-15', status: 'Scheduled', assigned_to: 'Dinesh Varma' }
        ]
        setActivities(list)
      } catch (err) {
        showToast('Failed to load activities', 'error')
      } finally {
        setLoading(false)
      }
    }
    loadActivities()
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gradient">Farm Operations & Activities</h1>
          <p className="text-sm text-muted">Log, schedule, and track daily field tasks</p>
        </div>
        <button onClick={() => showToast('Activity creation dialog', 'info')} className="btn btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Log New Activity
        </button>
      </div>

      {loading ? (
        <div className="card-glass p-6 text-center text-muted">Loading activities...</div>
      ) : (
        <div className="card-glass overflow-hidden">
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="border-b border-white/10 bg-white/5 text-muted text-xs uppercase font-semibold">
                <th className="p-4">Activity</th>
                <th className="p-4">Category</th>
                <th className="p-4">Target Plot</th>
                <th className="p-4">Assigned To</th>
                <th className="p-4">Scheduled Date</th>
                <th className="p-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {activities.map((act) => (
                <tr key={act.id} className="hover:bg-white/5 transition">
                  <td className="p-4 font-semibold text-white">{act.title}</td>
                  <td className="p-4 text-emerald-300">{act.category}</td>
                  <td className="p-4 text-muted">{act.plot}</td>
                  <td className="p-4 text-gray-200">{act.assigned_to}</td>
                  <td className="p-4 text-muted">{act.date}</td>
                  <td className="p-4">
                    <span className={`badge ${act.status === 'Completed' ? 'badge-success' : act.status === 'In Progress' ? 'badge-warning' : 'badge-info'}`}>
                      {act.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
