import React from 'react'
import { TrendingUp, BarChart3, PieChart, Activity, Droplets } from 'lucide-react'
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar } from 'recharts'

const yieldData = [
  { month: 'Jan', yield: 4.2, target: 4.0 },
  { month: 'Feb', yield: 4.8, target: 4.5 },
  { month: 'Mar', yield: 5.1, target: 4.8 },
  { month: 'Apr', yield: 5.6, target: 5.0 },
  { month: 'May', yield: 6.0, target: 5.2 },
  { month: 'Jun', yield: 6.4, target: 5.5 }
]

const waterUsageData = [
  { plot: 'Plot A', liters: 4500 },
  { plot: 'Plot B', liters: 3800 },
  { plot: 'Plot C', liters: 5200 },
  { plot: 'Plot D', liters: 3100 }
]

export default function Analytics() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gradient flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-emerald-400" /> Agronomic Analytics & Yield Insights
        </h1>
        <p className="text-sm text-muted">Comparative seasonal analytics, resource optimization, and yield forecasting</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card-glass p-6 space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold text-white">Crop Yield Performance (Tons / Acre)</h2>
            <span className="badge badge-success">+16.3% vs Target</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={yieldData}>
                <defs>
                  <linearGradient id="yieldGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="month" stroke="#9ca3af" fontSize={12} />
                <YAxis stroke="#9ca3af" fontSize={12} />
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                <Area type="monotone" dataKey="yield" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#yieldGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card-glass p-6 space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold text-white">Water Consumption Breakdown (Liters)</h2>
            <span className="badge badge-info">Drip Efficiency 94%</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={waterUsageData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="plot" stroke="#9ca3af" fontSize={12} />
                <YAxis stroke="#9ca3af" fontSize={12} />
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                <Bar dataKey="liters" fill="#06b6d4" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}
