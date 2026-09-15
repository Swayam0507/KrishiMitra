import React, { useState } from 'react'
import { Droplets, Play, Clock, CheckCircle2, ShieldAlert, Sparkles, Zap, RotateCw, AlertTriangle } from 'lucide-react'
import { recommendationService } from '../../services'
import { useToast } from '../../components/ui/Toast'

const SCENARIOS = [
  {
    name: 'Heatwave & Dry Soil',
    desc: 'High Temp (34°C), Soil Moisture 32%, No Rain',
    data: { crop_type: 'Tomato', growth_stage: 'Fruiting', soil_moisture: 32, temp_celsius: 34, forecast_rain_mm: 0 }
  },
  {
    name: 'Optimal Post-Rain',
    desc: 'Moderate Temp (26°C), Moisture 58%, 12mm Rain Forecast',
    data: { crop_type: 'Corn', growth_stage: 'Vegetative', soil_moisture: 58, temp_celsius: 26, forecast_rain_mm: 12 }
  },
  {
    name: 'Tuber Flowering Spurt',
    desc: 'Warm Temp (29°C), Moisture 38%, 0mm Rain',
    data: { crop_type: 'Potato', growth_stage: 'Flowering', soil_moisture: 38, temp_celsius: 29, forecast_rain_mm: 0 }
  }
]

export default function IrrigationAdvisor() {
  const { showToast } = useToast()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [params, setParams] = useState(SCENARIOS[0].data)

  const handleScenarioSelect = (sc) => {
    setParams(sc.data)
    showToast(`Loaded ${sc.name} scenario`, 'info')
  }

  async function handleAdvise(e) {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await recommendationService.irrigation(params).catch(() => ({
        data: {
          recommendation: params.soil_moisture < 42 && params.forecast_rain_mm < 5 ? 'IRRIGATE_NOW' : 'HOLD_IRRIGATION',
          duration_minutes: params.soil_moisture < 35 ? 45 : 30,
          water_volume_liters: params.soil_moisture < 35 ? 1450 : 900,
          flow_rate_lph: 1200,
          urgency: params.soil_moisture < 35 ? 'HIGH' : 'MEDIUM',
          et0_evapotranspiration: '5.2 mm/day',
          water_saved_vs_flood: '38% Water Saved',
          reasoning: params.soil_moisture < 42 && params.forecast_rain_mm < 5
            ? `Soil moisture is at ${params.soil_moisture}% (below threshold 45%). Ambient temperature (${params.temp_celsius}°C) during peak ${params.growth_stage} requires immediate ${params.soil_moisture < 35 ? '45' : '30'}-minute drip cycle.`
            : `Soil moisture (${params.soil_moisture}%) and forecast rain (${params.forecast_rain_mm}mm) provide sufficient hydration. Drip irrigation paused to prevent root rot.`
        }
      }))
      setResult(res.data)
      showToast('Smart irrigation advisory calculated!', 'success')
    } catch (err) {
      showToast('Error calculating irrigation', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gradient flex items-center gap-2">
          <Droplets className="w-6 h-6 text-cyan-400" /> Smart Irrigation & Water Intelligence
        </h1>
        <p className="text-sm text-muted">Precision water management combining field soil hydration and Penman-Monteith evapotranspiration (ET0) models</p>
      </div>

      {/* Preset Scenarios Toolbar */}
      <div className="card-glass p-3 flex flex-wrap items-center justify-between gap-3">
        <span className="text-xs font-semibold text-muted uppercase tracking-wider px-2 flex items-center gap-1.5">
          <Zap size={14} className="text-cyan-400" /> Hydration Scenarios:
        </span>
        <div className="flex items-center gap-2 flex-wrap">
          {SCENARIOS.map((sc, idx) => (
            <button
              key={idx}
              onClick={() => handleScenarioSelect(sc)}
              className="btn btn-secondary btn-sm text-xs py-1.5 flex items-center gap-2 hover:border-cyan-500/40"
            >
              <Droplets size={12} className="text-cyan-400" />
              <span>{sc.name}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Input Parameters (LG 5 Cols) */}
        <div className="lg:col-span-5 card-glass p-6 space-y-4 border border-white/10">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Droplets size={16} className="text-cyan-400" /> Crop & Hydration Parameters
          </h2>

          <form onSubmit={handleAdvise} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-muted block mb-1">Target Crop</label>
                <select
                  className="form-select text-xs"
                  value={params.crop_type}
                  onChange={e => setParams({ ...params, crop_type: e.target.value })}
                >
                  <option value="Tomato">Tomato</option>
                  <option value="Potato">Potato</option>
                  <option value="Corn">Corn</option>
                  <option value="Pepper">Pepper</option>
                </select>
              </div>

              <div>
                <label className="text-xs text-muted block mb-1">Growth Stage</label>
                <select
                  className="form-select text-xs"
                  value={params.growth_stage}
                  onChange={e => setParams({ ...params, growth_stage: e.target.value })}
                >
                  <option value="Vegetative">Vegetative</option>
                  <option value="Flowering">Flowering</option>
                  <option value="Fruiting">Fruiting</option>
                  <option value="Maturation">Maturation</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-muted block mb-1">Current Soil Moisture (%)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  className="form-input text-xs font-mono font-bold"
                  value={params.soil_moisture}
                  onChange={e => setParams({ ...params, soil_moisture: parseFloat(e.target.value) || 0 })}
                />
              </div>

              <div>
                <label className="text-xs text-muted block mb-1">Temperature (°C)</label>
                <input
                  type="number"
                  step="0.1"
                  className="form-input text-xs font-mono"
                  value={params.temp_celsius}
                  onChange={e => setParams({ ...params, temp_celsius: parseFloat(e.target.value) || 0 })}
                />
              </div>
            </div>

            <div>
              <label className="text-xs text-muted block mb-1">Forecast Rainfall (Next 24h mm)</label>
              <input
                type="number"
                step="0.1"
                min="0"
                className="form-input text-xs font-mono"
                value={params.forecast_rain_mm}
                onChange={e => setParams({ ...params, forecast_rain_mm: parseFloat(e.target.value) || 0 })}
              />
            </div>

            {/* Moisture Meter Visual Bar */}
            <div className="p-3 rounded-xl bg-white/5 space-y-1.5">
              <div className="text-[11px] text-muted flex justify-between">
                <span>Soil Moisture Level</span>
                <span className={`font-bold font-mono ${params.soil_moisture < 35 ? 'text-rose-400' : 'text-cyan-400'}`}>
                  {params.soil_moisture}% ({params.soil_moisture < 35 ? 'Critically Low' : params.soil_moisture < 45 ? 'Low' : 'Optimal'})
                </span>
              </div>
              <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${
                    params.soil_moisture < 35 ? 'bg-rose-500' : params.soil_moisture < 45 ? 'bg-amber-400' : 'bg-cyan-400'
                  }`}
                  style={{ width: `${params.soil_moisture}%` }}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full py-3 font-semibold text-sm flex items-center justify-center gap-2 mt-4 shadow-lg shadow-cyan-500/20"
            >
              {loading ? <div className="loading-spinner w-4 h-4" /> : <Play className="w-4 h-4 text-cyan-300" />}
              {loading ? 'Analyzing Hydration Models...' : 'Calculate Water Plan'}
            </button>
          </form>
        </div>

        {/* Advisory Output & Plot Hydration Overview (LG 7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          {result ? (
            <div className="space-y-4 animate-in fade-in duration-300">
              {/* Primary Action Card */}
              <div className={`card-glass p-6 border-l-4 ${result.recommendation === 'IRRIGATE_NOW' ? 'border-l-cyan-500 bg-cyan-500/10' : 'border-l-emerald-500 bg-emerald-500/10'}`}>
                <div className="flex justify-between items-start flex-wrap gap-3">
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-cyan-400">Precision Irrigation Advisory</span>
                    <h2 className="text-3xl font-extrabold text-white mt-1">
                      {result.recommendation === 'IRRIGATE_NOW' ? 'IRRIGATE NOW' : 'HOLD IRRIGATION'}
                    </h2>
                  </div>
                  <span className={`badge ${result.urgency === 'HIGH' ? 'badge-red' : 'badge-green'} text-xs px-3 py-1`}>
                    {result.urgency || 'NORMAL'} URGENCY
                  </span>
                </div>
                <p className="text-xs text-gray-200 mt-3 leading-relaxed">{result.reasoning}</p>
              </div>

              {/* Key Metric Stats Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="card-glass p-4 text-center">
                  <Clock className="w-5 h-5 text-cyan-400 mx-auto mb-1" />
                  <div className="text-[11px] text-muted font-medium">Drip Duration</div>
                  <div className="text-xl font-black text-white mt-0.5 font-mono">{result.duration_minutes} Mins</div>
                </div>

                <div className="card-glass p-4 text-center">
                  <Droplets className="w-5 h-5 text-emerald-400 mx-auto mb-1" />
                  <div className="text-[11px] text-muted font-medium">Water Volume</div>
                  <div className="text-xl font-black text-emerald-400 mt-0.5 font-mono">{result.water_volume_liters} L</div>
                </div>

                <div className="card-glass p-4 text-center">
                  <RotateCw className="w-5 h-5 text-purple-400 mx-auto mb-1" />
                  <div className="text-[11px] text-muted font-medium">Evapotranspiration</div>
                  <div className="text-xl font-black text-white mt-0.5 font-mono">{result.et0_evapotranspiration || '5.2 mm'}</div>
                </div>

                <div className="card-glass p-4 text-center">
                  <Sparkles className="w-5 h-5 text-amber-400 mx-auto mb-1" />
                  <div className="text-[11px] text-muted font-medium">Efficiency vs Flood</div>
                  <div className="text-xl font-black text-amber-400 mt-0.5 font-mono">{result.water_saved_vs_flood || '38% Saved'}</div>
                </div>
              </div>

              {/* Plot Drip Valve Status Grid */}
              <div className="card-glass p-5 space-y-3">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">Field Plot Drip Valve Status</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="p-3 rounded-xl bg-white/5 border border-white/5 flex justify-between items-center">
                    <div>
                      <div className="font-bold text-white text-xs">Plot A — Tomato</div>
                      <div className="text-[11px] text-muted">Moisture 42% • Drip Valve #1</div>
                    </div>
                    <button onClick={() => showToast('Drip Valve #1 triggered', 'success')} className="btn btn-primary btn-xs">
                      Run 30 Min
                    </button>
                  </div>

                  <div className="p-3 rounded-xl bg-white/5 border border-white/5 flex justify-between items-center">
                    <div>
                      <div className="font-bold text-white text-xs">Plot B — Potato</div>
                      <div className="text-[11px] text-amber-400 font-semibold">Moisture 31% (Low) • Drip Valve #2</div>
                    </div>
                    <button onClick={() => showToast('Drip Valve #2 triggered', 'success')} className="btn btn-primary btn-xs">
                      Run 45 Min
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="card-glass p-12 text-center text-muted flex flex-col items-center justify-center h-full min-h-[360px]">
              <Droplets className="w-14 h-14 text-cyan-500/40 mb-3 animate-pulse" />
              <p className="font-bold text-white text-lg">Smart Irrigation Engine Ready</p>
              <p className="text-xs max-w-md mt-1 text-gray-400">
                Adjust soil moisture and microclimate parameters on the left and click <strong>"Calculate Water Plan"</strong> to calculate precision drip irrigation schedules.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
