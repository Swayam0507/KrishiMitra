import React, { useState, useEffect } from 'react'
import {
  Activity, Database, Eye, TrendingUp, ShieldAlert, Cpu,
  CheckCircle, RotateCw, ChevronRight, Play, Pause, RefreshCw, Sparkles, Zap
} from 'lucide-react'
import { useToast } from '../components/ui/Toast'

const LOOP_STAGES = [
  {
    id: 'data',
    name: 'DATA INGESTION',
    icon: Database,
    color: 'text-cyan-400',
    bg: 'bg-cyan-500/10 border-cyan-500/30',
    shortDesc: 'Soil & climate data streams',
    model: 'OpenMeteo Weather API + Field Telemetry Engine',
    desc: 'Ingests field metrics (soil moisture 31% on Plot B, temp 28.4°C, pH 5.8) combined with 7-day OpenMeteo microclimate forecast.',
    inputs: ['Soil Moisture: 31%', 'Ambient Temp: 28.4°C', 'Humidity: 72%', 'Rain Probability: 15%'],
    status: 'Ingestion Active (120ms latency)'
  },
  {
    id: 'perception',
    name: 'PERCEPTION',
    icon: Eye,
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10 border-emerald-500/30',
    shortDesc: 'PyTorch Vision Model',
    model: 'PyTorch ResNet-50 Leaf Disease Classifier',
    desc: 'PyTorch Leaf Disease Vision model detects Early Blight (Alternaria solani) with 89.4% confidence on Plot B Potato foliage.',
    inputs: ['Leaf RGB Sample #1042', 'Confidence: 89.4%', 'Lesion Area: 14%'],
    status: 'Inference Complete'
  },
  {
    id: 'prediction',
    name: 'PREDICTION',
    icon: TrendingUp,
    color: 'text-purple-400',
    bg: 'bg-purple-500/10 border-purple-500/30',
    shortDesc: 'ET0 Evapotranspiration',
    model: 'Scikit-learn Yield & Water Loss Predictor',
    desc: 'Evapotranspiration models forecast a 14% soil moisture deficit over the next 36 hours due to rising temperatures.',
    inputs: ['Moisture Deficit: -14%', 'ET0 Rate: 5.2 mm/day', 'Transpiration Index: High'],
    status: 'Yield Impact Forecasted'
  },
  {
    id: 'risk',
    name: 'RISK MATRIX',
    icon: ShieldAlert,
    color: 'text-rose-400',
    bg: 'bg-rose-500/10 border-rose-500/30',
    shortDesc: 'Composite Farm Risk Score',
    model: 'Multi-Factor Risk Assessment Engine',
    desc: 'Composite farm risk matrix computes score at 74/100 (HIGH RISK for fungal blight expansion combined with moisture stress).',
    inputs: ['Pathogen Risk: High', 'Moisture Stress: High', 'Composite Risk: 74/100'],
    status: 'High Risk Alert Triggered'
  },
  {
    id: 'reasoning',
    name: 'AGENTIC REASONING',
    icon: Cpu,
    color: 'text-amber-400',
    bg: 'bg-amber-500/10 border-amber-500/30',
    shortDesc: 'Gemini LLM Farm Advisor',
    model: 'Google Gemini Pro Agentic Advisor',
    desc: 'Agentic Advisor evaluates 8 possible mitigation strategies. Balances immediate drip irrigation vs fungicide spray sequence.',
    inputs: ['Option A: Flood Irrigation', 'Option B: Drip + Copper Oxychloride', 'Chosen: Option B'],
    status: 'Action Sequence Formulated'
  },
  {
    id: 'decision',
    name: 'DECISION MATRIX',
    icon: CheckCircle,
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10 border-emerald-500/30',
    shortDesc: '45-Min Drip + Fungicide',
    model: 'Precision Agronomic Rule Engine',
    desc: 'Schedule 45-minute drip irrigation for Plot B at 06:00 AM followed by Copper Oxychloride spray application at 08:30 AM.',
    inputs: ['Drip Valve #2: 45 Mins (1,450L)', 'Spray Task: Ramesh Patel (08:30 AM)'],
    status: 'Task Schedule Approved'
  },
  {
    id: 'action',
    name: 'ACTION EXECUTION',
    icon: RotateCw,
    color: 'text-sky-400',
    bg: 'bg-sky-500/10 border-sky-500/30',
    shortDesc: 'Valve Command & Task Dispatch',
    model: 'Field Automation Controller',
    desc: 'Telemetry signal sent to Drip Valve #2; automated notification dispatches task to farm supervisor Ramesh Patel.',
    inputs: ['Signal: VALVE_OPEN_RELAY_2', 'SMS Notification Sent: +91 98765*****'],
    status: 'Valve Activated & Task Dispatched'
  },
  {
    id: 'monitoring',
    name: 'CLOSED-LOOP MONITORING',
    icon: Activity,
    color: 'text-indigo-400',
    bg: 'bg-indigo-500/10 border-indigo-500/30',
    shortDesc: 'Post-action Hydration Verification',
    model: 'Feedback Loop Telemetry Validator',
    desc: 'Field telemetry records post-irrigation soil hydration increase from 31% to 62%, confirming complete risk resolution.',
    inputs: ['Pre-Hydration: 31%', 'Post-Hydration: 62%', 'Risk Score: Reduced to 22/100'],
    status: 'Closed-Loop Optimization Verified'
  }
]

export default function IntelligenceLoop() {
  const { showToast } = useToast()
  const [selectedStage, setSelectedStage] = useState(LOOP_STAGES[0])
  const [isPlaying, setIsPlaying] = useState(false)

  useEffect(() => {
    let interval = null
    if (isPlaying) {
      interval = setInterval(() => {
        setSelectedStage(prev => {
          const currentIdx = LOOP_STAGES.findIndex(s => s.id === prev.id)
          const nextIdx = (currentIdx + 1) % LOOP_STAGES.length
          if (nextIdx === 0) {
            setIsPlaying(false)
            showToast('Simulated Intelligence Loop completed full cycle!', 'success')
          }
          return LOOP_STAGES[nextIdx]
        })
      }, 1800)
    }
    return () => clearInterval(interval)
  }, [isPlaying])

  const toggleSimulation = () => {
    setIsPlaying(!isPlaying)
    if (!isPlaying) showToast('Started automated Intelligence Cycle simulation', 'info')
  }

  const currentIdx = LOOP_STAGES.findIndex(s => s.id === selectedStage.id)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gradient flex items-center gap-2">
            <RotateCw className="w-6 h-6 text-emerald-400" /> End-to-End AgriFlow AI Intelligence Loop
          </h1>
          <p className="text-sm text-muted">Continuous closed-loop sense-reason-act agricultural feedback cycle</p>
        </div>

        <button
          onClick={toggleSimulation}
          className={`btn ${isPlaying ? 'btn-danger' : 'btn-primary'} flex items-center gap-2 text-xs font-semibold shadow-lg`}
        >
          {isPlaying ? <Pause size={14} /> : <Play size={14} />}
          <span>{isPlaying ? 'Pause Simulation' : 'Run Simulated Intelligence Cycle'}</span>
        </button>
      </div>

      {/* Progress Track */}
      <div className="card-glass p-3 flex items-center gap-4">
        <div className="text-xs font-bold text-muted uppercase tracking-wider whitespace-nowrap">
          Cycle Progress:
        </div>
        <div className="flex-1 bg-white/10 h-2.5 rounded-full overflow-hidden">
          <div
            className="bg-gradient-to-r from-cyan-400 via-emerald-400 to-amber-400 h-full transition-all duration-500"
            style={{ width: `${((currentIdx + 1) / LOOP_STAGES.length) * 100}%` }}
          />
        </div>
        <span className="text-xs font-mono font-bold text-emerald-400">
          Stage {currentIdx + 1} / {LOOP_STAGES.length}
        </span>
      </div>

      {/* 8-Stage Flowchart Nodes Grid */}
      <div className="card-glass p-6 overflow-x-auto border border-white/10">
        <div className="flex items-center justify-between min-w-[1000px] gap-2 py-2">
          {LOOP_STAGES.map((stage, idx) => {
            const Icon = stage.icon
            const isSelected = selectedStage.id === stage.id

            return (
              <React.Fragment key={stage.id}>
                <button
                  onClick={() => {
                    setSelectedStage(stage)
                    setIsPlaying(false)
                  }}
                  className={`flex flex-col items-center gap-2 p-3.5 rounded-2xl border transition-all duration-300 cursor-pointer min-w-[105px] ${stage.bg} ${
                    isSelected ? 'ring-2 ring-emerald-400 scale-105 shadow-xl shadow-emerald-500/20' : 'hover:scale-102 opacity-75 hover:opacity-100'
                  }`}
                >
                  <div className={`p-2.5 rounded-xl bg-black/50 ${stage.color}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-extrabold text-white tracking-wider text-center">{stage.name.split(' ')[0]}</span>
                </button>

                {idx < LOOP_STAGES.length - 1 && (
                  <ChevronRight className={`w-4 h-4 shrink-0 transition-colors ${idx < currentIdx ? 'text-emerald-400' : 'text-gray-700'}`} />
                )}
              </React.Fragment>
            )
          })}
        </div>
      </div>

      {/* Detailed Stage Inspector Panel */}
      <div className="card-glass p-6 border-l-4 border-l-emerald-500 space-y-4 animate-in fade-in duration-300">
        <div className="flex justify-between items-start flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <div className={`p-3 rounded-2xl bg-black/50 ${selectedStage.color}`}>
              <selectedStage.icon className="w-7 h-7" />
            </div>
            <div>
              <span className="text-xs font-bold text-muted uppercase tracking-wider">
                Stage {currentIdx + 1} of {LOOP_STAGES.length}
              </span>
              <h2 className="text-2xl font-black text-white">{selectedStage.name}</h2>
              <p className="text-xs text-emerald-400 font-semibold font-mono">{selectedStage.model}</p>
            </div>
          </div>

          <span className="badge badge-green text-xs font-mono py-1 px-3">
            {selectedStage.status}
          </span>
        </div>

        <p className="text-sm text-gray-200 leading-relaxed pt-2 border-t border-white/10">
          {selectedStage.desc}
        </p>

        {/* Inputs / Metrics Pills */}
        <div className="space-y-2 pt-2">
          <div className="text-xs font-bold text-muted uppercase tracking-wider">Live Telemetry & Model Artifacts:</div>
          <div className="flex flex-wrap gap-2">
            {selectedStage.inputs.map((inp, i) => (
              <span key={i} className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs font-mono text-gray-200">
                ⚡ {inp}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
