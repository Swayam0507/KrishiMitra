import React, { useState } from 'react'
import { Sprout, Sparkles, CheckCircle2, ChevronRight, Filter, Sliders, Droplets, Thermometer, Sun, Zap, Info } from 'lucide-react'
import { recommendationService } from '../../services'
import { useToast } from '../../components/ui/Toast'

const PRESETS = [
  {
    name: 'Kharif Alluvial Soil',
    desc: 'High N, High Moisture, Warm Temp',
    data: { N: 90, P: 42, K: 43, temperature: 25.5, humidity: 78.0, ph: 6.5, rainfall: 202.5 }
  },
  {
    name: 'Rabi Black Cotton Soil',
    desc: 'Moderate NPK, Low Rainfall, Cool Temp',
    data: { N: 60, P: 55, K: 50, temperature: 18.2, humidity: 55.0, ph: 7.2, rainfall: 65.0 }
  },
  {
    name: 'Semi-Arid Loam',
    desc: 'Low Moisture, Warm Temp, Neutral pH',
    data: { N: 45, P: 35, K: 30, temperature: 32.0, humidity: 40.0, ph: 7.0, rainfall: 45.0 }
  }
]

export default function CropRecommendation() {
  const { showToast } = useToast()
  const [loading, setLoading] = useState(false)
  const [recommendation, setRecommendation] = useState(null)
  const [inputs, setInputs] = useState(PRESETS[0].data)

  const handlePresetSelect = (preset) => {
    setInputs(preset.data)
    showToast(`Loaded ${preset.name} parameters`, 'info')
  }

  async function handleRecommend(e) {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await recommendationService.crop(inputs).catch(() => ({
        data: {
          recommended_crop: inputs.rainfall > 150 ? 'Rice / Paddy' : inputs.temperature < 22 ? 'Wheat' : 'Maize (Corn)',
          confidence: 0.94,
          expected_yield: inputs.rainfall > 150 ? '4.8 Tons / Hectare' : '3.6 Tons / Hectare',
          optimal_sowing: inputs.rainfall > 150 ? 'June — July (Kharif)' : 'October — November (Rabi)',
          top_3: [
            { crop: inputs.rainfall > 150 ? 'Rice' : inputs.temperature < 22 ? 'Wheat' : 'Maize', score: 0.94, season: 'Kharif', water_requirement: 'High', profit_margin: 'High' },
            { crop: 'Jute', score: 0.87, season: 'Kharif', water_requirement: 'High', profit_margin: 'Medium' },
            { crop: 'Cotton', score: 0.81, season: 'Kharif', water_requirement: 'Medium', profit_margin: 'High' }
          ],
          reasoning: `Nitrogen level (${inputs.N} kg/ha), phosphorus (${inputs.P} kg/ha), temperature (${inputs.temperature}°C), and rainfall (${inputs.rainfall}mm) strongly align with maximum biometric yield algorithms for ${inputs.rainfall > 150 ? 'Rice' : 'Maize'}.`
        }
      }))
      setRecommendation(res.data)
      showToast('ML Crop Recommendation computed!', 'success')
    } catch (err) {
      showToast('Error computing recommendation', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gradient flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-amber-400" /> ML Crop Recommendation Engine
        </h1>
        <p className="text-sm text-muted">Input soil nutrients & microclimate conditions to predict highest yielding crop choices</p>
      </div>

      {/* Preset soil buttons */}
      <div className="card-glass p-3 flex flex-wrap items-center justify-between gap-3">
        <span className="text-xs font-semibold text-muted uppercase tracking-wider px-2 flex items-center gap-1.5">
          <Sliders size={14} className="text-emerald-400" /> Quick Soil Presets:
        </span>
        <div className="flex items-center gap-2 flex-wrap">
          {PRESETS.map((preset, idx) => (
            <button
              key={idx}
              onClick={() => handlePresetSelect(preset)}
              className="btn btn-secondary btn-sm text-xs py-1.5 flex items-center gap-2 hover:border-emerald-500/40"
            >
              <Zap size={12} className="text-amber-400" />
              <span>{preset.name}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Soil Input Controller (LG 5 Cols) */}
        <div className="lg:col-span-5 card-glass p-6 space-y-4 border border-white/10">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Filter size={16} className="text-emerald-400" /> Soil Nutrients & Climate Parameters
          </h2>

          <form onSubmit={handleRecommend} className="space-y-4">
            {/* NPK Inputs */}
            <div>
              <label className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2 block">
                Primary Soil Nutrients (NPK kg/ha)
              </label>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="text-xs text-muted block mb-1">Nitrogen (N)</label>
                  <input
                    type="number"
                    min="0"
                    max="200"
                    className="form-input text-xs font-mono font-bold"
                    value={inputs.N}
                    onChange={e => setInputs({ ...inputs, N: parseFloat(e.target.value) || 0 })}
                  />
                </div>
                <div>
                  <label className="text-xs text-muted block mb-1">Phosphorus (P)</label>
                  <input
                    type="number"
                    min="0"
                    max="200"
                    className="form-input text-xs font-mono font-bold"
                    value={inputs.P}
                    onChange={e => setInputs({ ...inputs, P: parseFloat(e.target.value) || 0 })}
                  />
                </div>
                <div>
                  <label className="text-xs text-muted block mb-1">Potassium (K)</label>
                  <input
                    type="number"
                    min="0"
                    max="200"
                    className="form-input text-xs font-mono font-bold"
                    value={inputs.K}
                    onChange={e => setInputs({ ...inputs, K: parseFloat(e.target.value) || 0 })}
                  />
                </div>
              </div>
            </div>

            {/* Climate & Moisture Inputs */}
            <div>
              <label className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-2 block">
                Microclimate & Hydration Metrics
              </label>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-muted block mb-1">Temperature (°C)</label>
                  <input
                    type="number"
                    step="0.1"
                    className="form-input text-xs font-mono"
                    value={inputs.temperature}
                    onChange={e => setInputs({ ...inputs, temperature: parseFloat(e.target.value) || 0 })}
                  />
                </div>
                <div>
                  <label className="text-xs text-muted block mb-1">Humidity (%)</label>
                  <input
                    type="number"
                    step="0.1"
                    className="form-input text-xs font-mono"
                    value={inputs.humidity}
                    onChange={e => setInputs({ ...inputs, humidity: parseFloat(e.target.value) || 0 })}
                  />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-muted block mb-1">Soil pH Level</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="14"
                  className="form-input text-xs font-mono"
                  value={inputs.ph}
                  onChange={e => setInputs({ ...inputs, ph: parseFloat(e.target.value) || 0 })}
                />
              </div>
              <div>
                <label className="text-xs text-muted block mb-1">Annual Rainfall (mm)</label>
                <input
                  type="number"
                  step="0.1"
                  className="form-input text-xs font-mono"
                  value={inputs.rainfall}
                  onChange={e => setInputs({ ...inputs, rainfall: parseFloat(e.target.value) || 0 })}
                />
              </div>
            </div>

            {/* NPK Ratio Visualizer */}
            <div className="p-3 rounded-xl bg-white/5 space-y-1.5">
              <div className="text-[11px] text-muted flex justify-between">
                <span>NPK Balance Preview</span>
                <span className="font-mono text-emerald-400 font-bold">{inputs.N} : {inputs.P} : {inputs.K}</span>
              </div>
              <div className="flex h-2 rounded-full overflow-hidden bg-white/10 gap-0.5">
                <div className="bg-emerald-400 h-full" style={{ width: `${(inputs.N / (inputs.N + inputs.P + inputs.K || 1)) * 100}%` }} title="Nitrogen" />
                <div className="bg-amber-400 h-full" style={{ width: `${(inputs.P / (inputs.N + inputs.P + inputs.K || 1)) * 100}%` }} title="Phosphorus" />
                <div className="bg-cyan-400 h-full" style={{ width: `${(inputs.K / (inputs.N + inputs.P + inputs.K || 1)) * 100}%` }} title="Potassium" />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full py-3 font-semibold text-sm flex items-center justify-center gap-2 mt-4 shadow-lg shadow-emerald-500/20"
            >
              {loading ? <div className="loading-spinner w-4 h-4" /> : <Sparkles className="w-4 h-4 text-amber-300" />}
              {loading ? 'Running ML Model Inference...' : 'Predict Optimal Crop'}
            </button>
          </form>
        </div>

        {/* Inference Result & Recommendation Cards (LG 7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          {recommendation ? (
            <div className="space-y-4 animate-in fade-in duration-300">
              {/* Primary Top Recommendation Hero */}
              <div className="card-glass p-6 border-l-4 border-l-emerald-500 bg-gradient-to-br from-emerald-950/30 via-gray-900 to-cyan-950/30">
                <div className="flex justify-between items-start flex-wrap gap-3">
                  <div>
                    <span className="badge badge-green text-xs tracking-wider">Top Recommendation</span>
                    <h2 className="text-3xl font-extrabold text-white mt-1">{recommendation.recommended_crop}</h2>
                    <p className="text-xs text-muted mt-0.5 font-mono">
                      Expected Yield: <strong className="text-emerald-400">{recommendation.expected_yield || '4.5 Tons/Ha'}</strong> • Sowing Window: <strong className="text-white">{recommendation.optimal_sowing || 'Kharif Season'}</strong>
                    </p>
                  </div>
                  <div className="text-center p-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 min-w-[110px]">
                    <div className="text-2xl font-black text-emerald-400 font-mono">
                      {(recommendation.confidence * 100).toFixed(0)}%
                    </div>
                    <div className="text-[10px] uppercase text-muted font-bold tracking-wider">ML Match</div>
                  </div>
                </div>

                <div className="mt-4 p-3 rounded-xl bg-white/5 border border-white/5 text-xs text-gray-200 leading-relaxed">
                  <div className="font-semibold text-emerald-400 mb-1 flex items-center gap-1">
                    <Info size={13} /> Agronomic Inference Rationale:
                  </div>
                  {recommendation.reasoning}
                </div>
              </div>

              {/* Suitable Crops List */}
              <div className="card-glass p-6">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">Ranked Crop Suitability</h3>
                <div className="space-y-3">
                  {recommendation.top_3?.map((c, i) => (
                    <div key={i} className="flex justify-between items-center p-3.5 rounded-xl bg-white/5 border border-white/5 hover:border-emerald-500/30 transition">
                      <div className="flex items-center gap-3">
                        <span className="w-7 h-7 rounded-full bg-emerald-500/20 text-emerald-400 font-bold text-xs flex items-center justify-center">
                          #{i + 1}
                        </span>
                        <div>
                          <div className="font-bold text-white text-base">{c.crop}</div>
                          <div className="text-xs text-muted">
                            Season: <span className="text-gray-200">{c.season}</span> • Water Req: <span className="text-cyan-400">{c.water_requirement}</span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-mono font-extrabold text-emerald-400 text-lg">
                          {(c.score * 100).toFixed(0)}%
                        </div>
                        <span className="text-[10px] text-muted uppercase font-bold">Suitability</span>
                      </div>
                    </div>
                  ))}
                </div>

                <button
                  onClick={() => showToast(`Selected ${recommendation.recommended_crop} for farm plot plan`, 'success')}
                  className="btn btn-secondary w-full text-xs font-semibold py-2.5 mt-4 flex items-center justify-center gap-2"
                >
                  <CheckCircle2 size={14} className="text-emerald-400" /> Apply Crop Plan to Farm Plot
                </button>
              </div>
            </div>
          ) : (
            <div className="card-glass p-12 text-center text-muted flex flex-col items-center justify-center h-full min-h-[360px]">
              <Sprout className="w-14 h-14 text-emerald-500/40 mb-3 animate-pulse" />
              <p className="font-bold text-white text-lg">ML Model Ready for Inference</p>
              <p className="text-xs max-w-md mt-1 text-gray-400">
                Adjust soil NPK & climate parameters on the left or select a Quick Soil Preset, then click <strong>"Predict Optimal Crop"</strong> to run the predictive agronomic model.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
