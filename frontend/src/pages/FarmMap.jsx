import React, { useState } from 'react'
import {
  MapPin, Layers, Info, Sun, Droplets, Eye, ShieldAlert,
  Sprout, Thermometer, Wind, Compass, Sparkles, ChevronRight, X
} from 'lucide-react'
import { useToast } from '../components/ui/Toast'

const MAP_LAYERS = [
  { id: 'hybrid', name: 'Satellite Hybrid', icon: Compass, badge: 'HD Satellite' },
  { id: 'ndvi', name: 'NDVI Vegetation Health', icon: Eye, badge: 'Vegetation Index' },
  { id: 'moisture', name: 'Soil Moisture Gradient', icon: Droplets, badge: 'Hydration' },
  { id: 'elevation', name: 'Topography & Contour', icon: Layers, badge: 'Elevation' },
]

const PLOTS = [
  {
    id: 'plot-a',
    name: 'Plot A — North Sector',
    crop: 'Tomato (Hybrid Red)',
    variety: 'Heirloom San Marzano',
    stage: 'Fruiting Phase',
    area: '2.5 Acres',
    moisture: 42,
    moistureStatus: 'Optimal',
    healthScore: 92,
    ndviScore: '0.84 (Dense Canopy)',
    soilPh: 6.4,
    npk: 'N:90 P:42 K:43 (kg/ha)',
    riskLevel: 'Low',
    color: '#10b981',
    svgPath: 'M 40,40 L 440,30 L 430,230 L 30,220 Z',
    labelPos: { x: 220, y: 130 },
    temperature: '26.8°C',
    humidity: '68%',
    recommendation: 'Scheduled drip cycle tomorrow at 06:00 AM (30 min)'
  },
  {
    id: 'plot-b',
    name: 'Plot B — East Sector',
    crop: 'Potato (Kufri Jyoti)',
    variety: 'Early Maturing Tuber',
    stage: 'Tuber Initiation',
    area: '2.5 Acres',
    moisture: 31,
    moistureStatus: 'Low Hydration',
    healthScore: 74,
    ndviScore: '0.62 (Moderate Growth)',
    soilPh: 5.8,
    npk: 'N:65 P:30 K:50 (kg/ha)',
    riskLevel: 'Medium (Blight Vulnerable)',
    color: '#f59e0b',
    svgPath: 'M 450,30 L 860,20 L 850,220 L 440,230 Z',
    labelPos: { x: 640, y: 130 },
    temperature: '28.4°C',
    humidity: '72%',
    recommendation: 'Immediate 45-min drip cycle recommended + Fungicide preventive spray'
  },
  {
    id: 'plot-c',
    name: 'Plot C — South-West Sector',
    crop: 'Corn (Sweet Maize)',
    variety: 'Pioneer Hybrid 3397',
    stage: 'Vegetative Growth',
    area: '2.5 Acres',
    moisture: 55,
    moistureStatus: 'Optimal',
    healthScore: 96,
    ndviScore: '0.91 (Vigorous Canopy)',
    soilPh: 6.7,
    npk: 'N:110 P:48 K:60 (kg/ha)',
    riskLevel: 'Optimal Health',
    color: '#06b6d4',
    svgPath: 'M 30,230 L 430,240 L 420,440 L 20,430 Z',
    labelPos: { x: 220, y: 340 },
    temperature: '25.9°C',
    humidity: '64%',
    recommendation: 'Soil nitrogen optimal. Maintain current irrigation frequency.'
  },
  {
    id: 'plot-d',
    name: 'Plot D — South-East Sector',
    crop: 'Bell Pepper (Capsicum)',
    variety: 'California Wonder',
    stage: 'Flowering & Setting',
    area: '2.5 Acres',
    moisture: 45,
    moistureStatus: 'Optimal',
    healthScore: 88,
    ndviScore: '0.78 (Healthy Crop)',
    soilPh: 6.5,
    npk: 'N:85 P:38 K:45 (kg/ha)',
    riskLevel: 'Low',
    color: '#8b5cf6',
    svgPath: 'M 440,240 L 850,230 L 840,430 L 430,440 Z',
    labelPos: { x: 630, y: 340 },
    temperature: '27.1°C',
    humidity: '65%',
    recommendation: 'Foliar micronutrient spray scheduled for Wednesday morning.'
  }
]

export default function FarmMap() {
  const { showToast } = useToast()
  const [activeLayer, setActiveLayer] = useState('hybrid')
  const [selectedPlot, setSelectedPlot] = useState(PLOTS[0])
  const [hoveredPlot, setHoveredPlot] = useState(null)
  const [filterRisk, setFilterRisk] = useState('all')

  const filteredPlots = PLOTS.filter(plot => {
    if (filterRisk === 'low') return plot.moisture >= 40
    if (filterRisk === 'warning') return plot.moisture < 40
    return true
  })

  const getLayerBackground = () => {
    switch (activeLayer) {
      case 'ndvi':
        return 'radial-gradient(circle at 50% 50%, rgba(16, 185, 129, 0.25), rgba(6, 182, 212, 0.15), rgba(6, 13, 26, 0.95))'
      case 'moisture':
        return 'radial-gradient(circle at 30% 40%, rgba(6, 182, 212, 0.3), rgba(59, 130, 246, 0.15), rgba(6, 13, 26, 0.95))'
      case 'elevation':
        return 'radial-gradient(circle at 70% 30%, rgba(245, 158, 11, 0.2), rgba(139, 92, 246, 0.15), rgba(6, 13, 26, 0.95))'
      default:
        return 'radial-gradient(circle at 50% 50%, rgba(12, 35, 64, 0.6), rgba(5, 46, 22, 0.4), rgba(6, 13, 26, 0.98))'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gradient flex items-center gap-2">
            <MapPin className="w-6 h-6 text-emerald-400" /> Interactive Spatial Farm Map
          </h1>
          <p className="text-sm text-muted">Geospatial parcel visualization & plot-level field diagnostics</p>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <div className="card-glass px-3 py-1.5 flex items-center gap-2 text-xs font-semibold text-emerald-400 border border-emerald-500/20">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            10.0 Acres Total • Ahmedabad, GJ
          </div>
          <button
            onClick={() => showToast('Refreshed spatial telemetry', 'success')}
            className="btn btn-secondary btn-sm"
          >
            Refresh Map
          </button>
        </div>
      </div>

      {/* Layer selector bar */}
      <div className="card-glass p-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 overflow-x-auto">
          <span className="text-xs font-semibold text-muted uppercase tracking-wider px-2">Map View Layer:</span>
          {MAP_LAYERS.map(layer => {
            const Icon = layer.icon
            const isActive = activeLayer === layer.id
            return (
              <button
                key={layer.id}
                onClick={() => setActiveLayer(layer.id)}
                className={`btn btn-sm flex items-center gap-2 transition-all ${
                  isActive
                    ? 'btn-primary shadow-lg shadow-emerald-500/20'
                    : 'btn-secondary text-gray-300 hover:text-white'
                }`}
              >
                <Icon size={14} />
                <span>{layer.name}</span>
                {isActive && <span className="text-[10px] bg-white/20 px-1.5 py-0.5 rounded font-mono">{layer.badge}</span>}
              </button>
            )
          })}
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-muted">Filter Parcels:</span>
          <select
            value={filterRisk}
            onChange={e => setFilterRisk(e.target.value)}
            className="form-select py-1 px-3 text-xs w-auto"
          >
            <option value="all">All Parcels (4)</option>
            <option value="low">Optimal Hydration</option>
            <option value="warning">Low Hydration / At Risk</option>
          </select>
        </div>
      </div>

      {/* Map Grid Container */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Spatial Map Canvas (LG 8 Cols) */}
        <div className="lg:col-span-8 card-glass p-4 relative overflow-hidden border border-white/10 flex flex-col justify-between" style={{ minHeight: '520px', background: getLayerBackground() }}>
          
          {/* Top Info Overlay */}
          <div className="flex justify-between items-start z-10 p-2">
            <div className="space-y-1">
              <span className="badge badge-green text-xs font-bold">AgriFlow Demo Farm Parcel Cluster</span>
              <div className="text-xs text-muted font-mono">GPS Bounds: 23.0225° N, 72.5714° E • Elevation: 53m</div>
            </div>

            {/* Layer Legend */}
            <div className="card-glass p-2.5 text-xs space-y-1 bg-black/70 border-white/10 backdrop-blur-md rounded-xl">
              <div className="text-[11px] font-bold text-gray-300 uppercase tracking-wider mb-1">Parcel Overview</div>
              <div className="flex items-center gap-2 text-emerald-400 font-semibold"><span className="w-2.5 h-2.5 rounded-full bg-emerald-400" /> Plot A (Tomato - 92% Health)</div>
              <div className="flex items-center gap-2 text-amber-400 font-semibold"><span className="w-2.5 h-2.5 rounded-full bg-amber-400" /> Plot B (Potato - Low Hydration)</div>
              <div className="flex items-center gap-2 text-cyan-400 font-semibold"><span className="w-2.5 h-2.5 rounded-full bg-cyan-400" /> Plot C (Corn - 96% Health)</div>
              <div className="flex items-center gap-2 text-purple-400 font-semibold"><span className="w-2.5 h-2.5 rounded-full bg-purple-400" /> Plot D (Pepper - 88% Health)</div>
            </div>
          </div>

          {/* SVG Map Canvas */}
          <div className="relative my-4 flex-1 flex items-center justify-center min-h-[360px]">
            <svg viewBox="0 0 880 470" className="w-full h-full max-h-[440px] drop-shadow-2xl">
              <defs>
                <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="1" />
                </pattern>
                
                {/* Glow Filter */}
                <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="6" result="blur" />
                  <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
              </defs>

              <rect width="880" height="470" fill="url(#grid)" rx="12" />

              {/* Render Plots */}
              {PLOTS.map(plot => {
                const isSelected = selectedPlot?.id === plot.id
                const isHovered = hoveredPlot === plot.id
                const isFilteredOut = filterRisk === 'low' ? plot.moisture < 40 : filterRisk === 'warning' ? plot.moisture >= 40 : false

                return (
                  <g
                    key={plot.id}
                    onClick={() => setSelectedPlot(plot)}
                    onMouseEnter={() => setHoveredPlot(plot.id)}
                    onMouseLeave={() => setHoveredPlot(null)}
                    className="cursor-pointer transition-all duration-300"
                    opacity={isFilteredOut ? 0.25 : 1}
                  >
                    <path
                      d={plot.svgPath}
                      fill={activeLayer === 'ndvi' ? plot.color + '44' : activeLayer === 'moisture' ? '#06b6d433' : plot.color + '22'}
                      stroke={plot.color}
                      strokeWidth={isSelected ? 3.5 : isHovered ? 2.5 : 1.5}
                      strokeDasharray={isSelected ? 'none' : isHovered ? '4,4' : 'none'}
                      filter={isSelected || isHovered ? 'url(#glow)' : 'none'}
                    />

                    {/* Label Overlay */}
                    <g transform={`translate(${plot.labelPos.x}, ${plot.labelPos.y})`}>
                      <rect
                        x="-75"
                        y="-26"
                        width="150"
                        height="52"
                        rx="8"
                        fill="rgba(6, 13, 26, 0.85)"
                        stroke={plot.color}
                        strokeWidth={isSelected ? "2" : "1"}
                      />
                      <text x="0" y="-8" textAnchor="middle" fill="#ffffff" fontSize="12" fontWeight="700">
                        {plot.name.split('—')[0].trim()}
                      </text>
                      <text x="0" y="8" textAnchor="middle" fill={plot.color} fontSize="11" fontWeight="600">
                        {plot.crop.split('(')[0].trim()}
                      </text>
                      <text x="0" y="20" textAnchor="middle" fill="#94a3b8" fontSize="10">
                        Moisture: {plot.moisture}%
                      </text>
                    </g>
                  </g>
                )
              })}
            </svg>
          </div>

          {/* Bottom Controls / Status Bar */}
          <div className="z-10 flex flex-wrap items-center justify-between gap-2 p-2 text-xs text-muted bg-black/40 rounded-xl border border-white/5">
            <div className="flex items-center gap-2">
              <Info className="w-4 h-4 text-emerald-400" />
              <span>Click any plot parcel to open detailed soil & field diagnostics.</span>
            </div>
            <div className="flex items-center gap-4">
              <span>Selected: <strong className="text-white">{selectedPlot ? selectedPlot.name : 'None'}</strong></span>
              <span>Active Layer: <strong className="text-emerald-400 capitalize">{activeLayer}</strong></span>
            </div>
          </div>
        </div>

        {/* Plot Diagnostics Panel (LG 4 Cols) */}
        <div className="lg:col-span-4 space-y-4">
          {selectedPlot ? (
            <div className="card-glass p-6 border-l-4 border-l-emerald-500 space-y-5 animate-in fade-in duration-300">
              <div className="flex justify-between items-start">
                <div>
                  <span className="badge badge-green text-xs">{selectedPlot.area} Parcel</span>
                  <h2 className="text-xl font-bold text-white mt-1">{selectedPlot.name}</h2>
                  <p className="text-xs text-emerald-400 font-semibold">{selectedPlot.crop}</p>
                </div>
                <button
                  onClick={() => setSelectedPlot(null)}
                  className="btn btn-ghost btn-icon text-gray-400 hover:text-white"
                  title="Close panel"
                >
                  <X size={18} />
                </button>
              </div>

              {/* Stat Grid */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                  <div className="text-xs text-gray-300 font-semibold flex items-center gap-1">
                    <Droplets size={12} className="text-cyan-400" /> Moisture Level
                  </div>
                  <div className="text-2xl font-extrabold text-white mt-1">{selectedPlot.moisture}%</div>
                  <div className={`text-[11px] font-semibold mt-0.5 ${selectedPlot.moisture < 40 ? 'text-amber-400' : 'text-emerald-400'}`}>
                    {selectedPlot.moistureStatus}
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-white/5 border border-white/10">
                  <div className="text-xs text-gray-300 font-semibold flex items-center gap-1">
                    <Sprout size={12} className="text-emerald-400" /> Health Score
                  </div>
                  <div className="text-2xl font-extrabold text-emerald-400 mt-1">{selectedPlot.healthScore}/100</div>
                  <div className="text-[11px] text-gray-400 mt-0.5 font-mono">{selectedPlot.ndviScore.split(' ')[0]} NDVI</div>
                </div>
              </div>

              {/* Structured Key Metrics Grid */}
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2.5 rounded-lg bg-white/5 border border-white/10">
                  <div className="text-[11px] text-gray-300 font-semibold uppercase tracking-wider">Growth Stage</div>
                  <div className="font-bold text-white mt-0.5">{selectedPlot.stage}</div>
                </div>

                <div className="p-2.5 rounded-lg bg-white/5 border border-white/10">
                  <div className="text-[11px] text-gray-300 font-semibold uppercase tracking-wider">Crop Variety</div>
                  <div className="font-bold text-white mt-0.5 truncate">{selectedPlot.variety}</div>
                </div>

                <div className="p-2.5 rounded-lg bg-white/5 border border-white/10">
                  <div className="text-[11px] text-gray-300 font-semibold uppercase tracking-wider">Soil pH Level</div>
                  <div className="font-bold text-emerald-400 font-mono mt-0.5">{selectedPlot.soilPh} pH (Optimal)</div>
                </div>

                <div className="p-2.5 rounded-lg bg-white/5 border border-white/10">
                  <div className="text-[11px] text-gray-300 font-semibold uppercase tracking-wider">Nutrient N-P-K</div>
                  <div className="font-bold text-cyan-400 font-mono mt-0.5">{selectedPlot.npk}</div>
                </div>

                <div className="p-2.5 rounded-lg bg-white/5 border border-white/10">
                  <div className="text-[11px] text-gray-300 font-semibold uppercase tracking-wider">Microclimate</div>
                  <div className="font-bold text-white mt-0.5">{selectedPlot.temperature}</div>
                </div>

                <div className="p-2.5 rounded-lg bg-white/5 border border-white/10">
                  <div className="text-[11px] text-gray-300 font-semibold uppercase tracking-wider">Risk Level</div>
                  <div className={`font-bold mt-0.5 ${selectedPlot.riskLevel.includes('Medium') ? 'text-amber-400' : 'text-emerald-400'}`}>
                    {selectedPlot.riskLevel}
                  </div>
                </div>
              </div>

              {/* Recommendation Box */}
              <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs">
                <div className="flex items-center gap-1.5 text-emerald-400 font-bold mb-1">
                  <Sparkles size={14} /> AI Recommendation
                </div>
                <p className="text-gray-200 leading-relaxed">{selectedPlot.recommendation}</p>
              </div>

              {/* Action Buttons */}
              <div className="space-y-2 pt-1">
                <button
                  onClick={() => showToast(`Irrigation triggered for ${selectedPlot.name}`, 'success')}
                  className="btn btn-primary w-full text-xs font-semibold py-2.5 flex items-center justify-center gap-2"
                >
                  <Droplets size={14} /> Trigger Direct Drip Irrigation
                </button>
                <button
                  onClick={() => showToast(`Opening logs for ${selectedPlot.name}`, 'info')}
                  className="btn btn-secondary w-full text-xs font-semibold py-2 flex items-center justify-center gap-2 text-gray-300"
                >
                  View Plot Diagnostics & Log
                </button>
              </div>
            </div>
          ) : (
            <div className="card-glass p-8 text-center text-muted flex flex-col items-center justify-center h-full min-h-[300px]">
              <MapPin className="w-12 h-12 text-emerald-500/40 mb-3" />
              <p className="font-medium text-white">Select a Parcel</p>
              <p className="text-xs max-w-xs mt-1">Click on any field parcel (Plot A, B, C, or D) on the map to inspect crop metrics and trigger precision field actions.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
