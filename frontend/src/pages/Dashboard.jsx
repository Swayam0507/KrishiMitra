import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Sprout, AlertCircle, Droplets, Activity, TrendingUp,
  TrendingDown, Leaf, Cloud, RefreshCw, ChevronRight, Zap
} from 'lucide-react'
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts'
import { farmService, alertService, intelligenceService, weatherService } from '../services'
import { useAuth } from '../context/AuthContext'
import { useLanguage } from '../context/LanguageContext'
import { useToast } from '../components/ui/Toast'

const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']

function StatCard({ icon, label, value, unit, color, trend, trendLabel }) {
  return (
    <div className="stat-card">
      <div className="stat-card-top">
        <div className="stat-icon" style={{ background: `${color}22`, color }}>
          {icon}
        </div>
        {trend != null && (
          <span className={`stat-trend ${trend >= 0 ? 'up' : 'down'}`}>
            {trend >= 0 ? <TrendingUp size={11} /> : <TrendingDown size={11} />}
            {Math.abs(trend)}%
          </span>
        )}
      </div>
      <div>
        <div className="stat-value">
          {value ?? '—'}{unit && <span style={{ fontSize: 16, color: 'var(--text-muted)' }}>{unit}</span>}
        </div>
        <div className="stat-label">{label}</div>
        {trendLabel && <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>{trendLabel}</div>}
      </div>
    </div>
  )
}

function RecommendationCard({ rec }) {
  const pColors = { Critical: 'var(--accent-red)', High: 'var(--accent-amber)', Medium: 'var(--accent-blue)', Low: 'var(--accent-green)' }
  return (
    <div className="card" style={{ borderLeft: `3px solid ${pColors[rec.priority] || 'var(--border-subtle)'}`, padding: '14px 16px' }}>
      <div className="flex items-center justify-between mb-2">
        <span className={`badge ${rec.priority === 'Critical' ? 'badge-red' : rec.priority === 'High' ? 'badge-amber' : rec.priority === 'Medium' ? 'badge-blue' : 'badge-green'}`}>
          {rec.priority}
        </span>
        <span className="text-xs text-muted">{rec.source}</span>
      </div>
      <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4 }}>{rec.title}</div>
      <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{rec.reason}</div>
      <div style={{ marginTop: 8, fontSize: 12, color: 'var(--accent-green)', fontWeight: 600 }}>
        → {rec.recommendedAction}
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { user } = useAuth()
  const { t } = useLanguage()
  const toast = useToast()

  const [farms, setFarms] = useState([])
  const [alerts, setAlerts] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [weather, setWeather] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedFarm, setSelectedFarm] = useState(null)

  useEffect(() => {
    loadAll()
  }, [])

  const loadAll = async () => {
    setLoading(true)
    try {
      const [farmsRes, alertsRes, weatherRes] = await Promise.allSettled([
        farmService.list(),
        alertService.list({ read: false, limit: 5 }),
        weatherService.current({}),
      ])

      const farmsData = farmsRes.status === 'fulfilled' ? farmsRes.value.data : []
      setFarms(farmsData)

      if (alertsRes.status === 'fulfilled') setAlerts(alertsRes.value.data || [])
      if (weatherRes.status === 'fulfilled') setWeather(weatherRes.value.data)

      if (farmsData.length > 0) {
        const firstFarm = farmsData[0]
        setSelectedFarm(firstFarm)

        const recs = await intelligenceService.recommendations(firstFarm.id).catch(() => ({ data: { recommendations: [] } }))
        setRecommendations(recs.data?.recommendations || [])
      }
    } catch (e) {
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const criticalAlerts = alerts.filter(a => a.priority === 'Critical' || a.priority === 'High')

  // Mock chart data (would come from real history in production)
  const healthTrendData = [
    { month: 'Apr', score: 62 }, { month: 'May', score: 68 },
    { month: 'Jun', score: 71 }, { month: 'Jul', score: 65 },
    { month: 'Aug', score: 74 }, { month: 'Sep', score: 78 },
  ]

  const cropDistData = farms.length > 0
    ? [{ name: 'Tomato', value: 35 }, { name: 'Potato', value: 25 }, { name: 'Corn', value: 25 }, { name: 'Other', value: 15 }]
    : []

  if (loading) return (
    <div className="loading-overlay">
      <div className="loading-spinner" style={{ width: 40, height: 40 }} />
      <span>Loading your farm intelligence...</span>
    </div>
  )

  return (
    <div>
      {/* Top Stats */}
      <div className="grid-4 mb-4">
        <StatCard icon={<Sprout size={22} />} label="Indicative Farm Health" value={selectedFarm ? '74' : '—'} unit="/100" color="var(--accent-green)" trend={4} trendLabel="vs. last month" />
        <StatCard icon={<Leaf size={22} />} label="Active Crops" value={farms.length > 0 ? '4' : '0'} color="var(--accent-emerald)" />
        <StatCard icon={<AlertCircle size={22} />} label="Active Alerts" value={alerts.length} color={alerts.length > 0 ? 'var(--accent-red)' : 'var(--accent-green)'} />
        <StatCard icon={<Droplets size={22} />} label="Water Efficiency" value="78" unit="%" color="var(--accent-blue)" trendLabel="Drip irrigation" />
      </div>

      {/* Weather Snapshot */}
      {weather && (
        <div className="card mb-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Cloud size={16} style={{ color: 'var(--accent-blue)' }} />
              <span style={{ fontWeight: 600, fontSize: 14 }}>Microclimate & Weather — {weather.city || 'Farm Location'}</span>
            </div>
            <Link to="/weather" className="text-sm text-green">View 7-Day Forecast →</Link>
          </div>
          <div className="flex items-center gap-6 flex-wrap">
            <div style={{ fontSize: 42, fontWeight: 800, fontFamily: 'Space Grotesk', color: 'var(--text-primary)' }}>
              {weather.temperature?.toFixed(0)}°C
            </div>
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, textTransform: 'capitalize', color: 'var(--text-primary)' }}>{weather.description}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Relative Humidity: {weather.humidity}% • Wind: {weather.windSpeed} km/h</div>
            </div>
          </div>
          {weather.recommendations?.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 12 }}>
              {weather.recommendations.slice(0, 2).map((r, i) => (
                <div key={i} style={{ fontSize: 12, color: 'var(--text-secondary)', padding: '6px 10px', background: 'var(--bg-secondary)', borderRadius: 8 }}>
                  💡 {r}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Charts row */}
      <div className="grid-2 mb-4">
        <div className="chart-container">
          <div className="chart-title">Farm Health Trend <span className="text-xs text-muted">(Indicative)</span></div>
          <ResponsiveContainer width="100%" height={160}>
            <AreaChart data={healthTrendData}>
              <defs>
                <linearGradient id="healthGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#22c55e" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="month" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} />
              <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} />
              <Tooltip
                contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: 8, color: 'var(--text-primary)', fontSize: 13 }}
                formatter={(v) => [`${v}/100`, 'Health Score']}
              />
              <Area type="monotone" dataKey="score" stroke="#22c55e" strokeWidth={2} fill="url(#healthGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {cropDistData.length > 0 ? (
          <div className="chart-container">
            <div className="chart-title">Crop Distribution</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <ResponsiveContainer width={140} height={140}>
                <PieChart>
                  <Pie data={cropDistData} cx="50%" cy="50%" innerRadius={40} outerRadius={65} dataKey="value" paddingAngle={3}>
                    {cropDistData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
              <div style={{ flex: 1 }}>
                {cropDistData.map((d, i) => (
                  <div key={d.name} className="flex items-center gap-2 mb-2">
                    <div style={{ width: 10, height: 10, borderRadius: '50%', background: COLORS[i % COLORS.length], flexShrink: 0 }} />
                    <span style={{ fontSize: 13, flex: 1 }}>{d.name}</span>
                    <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>{d.value}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="chart-container flex items-center justify-center" style={{ minHeight: 180 }}>
            <div className="empty-state" style={{ padding: 20 }}>
              <div className="empty-state-icon">🌱</div>
              <h3>No crops yet</h3>
              <p>Add farms and crops to see distribution</p>
              <Link to="/farms" className="btn btn-primary btn-sm mt-3">Add Farm</Link>
            </div>
          </div>
        )}
      </div>

      {/* Recommendations + Alerts */}
      <div className="grid-2-1 mb-4">
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Zap size={16} style={{ color: 'var(--accent-amber)' }} />
              <h3 style={{ fontSize: 15, fontWeight: 600 }}>AI Recommendations</h3>
            </div>
            {selectedFarm && (
              <button className="btn btn-ghost btn-sm" onClick={() => intelligenceService.recommendations(selectedFarm.id).then(r => setRecommendations(r.data.recommendations || []))}>
                <RefreshCw size={13} />
              </button>
            )}
          </div>
          {recommendations.length === 0 ? (
            <div className="empty-state" style={{ padding: '24px 0' }}>
              <div style={{ fontSize: 32 }}>✅</div>
              <p>{farms.length === 0 ? 'Add a farm to get recommendations.' : 'No recommendations at this time.'}</p>
              {farms.length === 0 && <Link to="/farms" className="btn btn-primary btn-sm mt-3">Add Farm</Link>}
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {recommendations.slice(0, 4).map((r, i) => <RecommendationCard key={i} rec={r} />)}
              {recommendations.length > 4 && (
                <Link to="/advisor" className="btn btn-ghost btn-sm" style={{ justifyContent: 'center' }}>
                  View all {recommendations.length} <ChevronRight size={14} />
                </Link>
              )}
            </div>
          )}
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <AlertCircle size={16} style={{ color: 'var(--accent-red)' }} />
              <h3 style={{ fontSize: 15, fontWeight: 600 }}>Critical Alerts</h3>
            </div>
            <Link to="/alerts" className="text-sm text-green">View all</Link>
          </div>
          {criticalAlerts.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '20px 0', color: 'var(--text-muted)', fontSize: 13 }}>
              <div style={{ fontSize: 32, marginBottom: 8 }}>✅</div>
              No critical alerts
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {criticalAlerts.slice(0, 5).map(a => (
                <div key={a.id} className={`card risk-card-${a.priority.toLowerCase()}`} style={{ padding: '12px 14px' }}>
                  <div className="flex items-center justify-between mb-1">
                    <span className={`badge ${a.priority === 'Critical' ? 'badge-red' : 'badge-amber'}`}>{a.priority}</span>
                    <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{a.type}</span>
                  </div>
                  <div style={{ fontSize: 13, fontWeight: 600 }}>{a.title}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>{a.message.substring(0, 80)}...</div>
                </div>
              ))}
            </div>
          )}

          <hr className="divider" />

          {/* Quick links */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <h4 style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 4 }}>Quick Actions</h4>
            {[
              { label: '🔬 Detect Disease', to: '/disease' },
              { label: '💧 Irrigation Advice', to: '/irrigation' },
              { label: '🤖 Run AI Advisor', to: '/advisor' },
              { label: '💬 Ask Assistant', to: '/assistant' },
            ].map(link => (
              <Link key={link.to} to={link.to} className="btn btn-secondary btn-sm" style={{ justifyContent: 'flex-start', fontWeight: 500 }}>
                {link.label}
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* No farms CTA */}
      {farms.length === 0 && (
        <div style={{ background: 'linear-gradient(135deg, rgba(34,197,94,0.1) 0%, rgba(16,185,129,0.05) 100%)', border: '1px solid rgba(34,197,94,0.2)', borderRadius: 16, padding: 32, textAlign: 'center' }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>🌾</div>
          <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8 }}>Set up your first farm</h2>
          <p style={{ color: 'var(--text-secondary)', maxWidth: 400, margin: '0 auto 24px' }}>
            Add your farm details to unlock AI disease detection, crop recommendations, irrigation intelligence, and more.
          </p>
          <div className="flex gap-3" style={{ justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/farms" className="btn btn-primary btn-lg">🌱 Add My Farm</Link>
            <Link to="/disease" className="btn btn-secondary btn-lg">🔬 Try Disease Detection</Link>
          </div>
        </div>
      )}
    </div>
  )
}
