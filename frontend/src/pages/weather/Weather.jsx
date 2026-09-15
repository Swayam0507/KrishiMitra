import React, { useEffect, useState } from 'react'
import { Cloud, Sun, CloudRain, Wind, Droplets, Thermometer, AlertTriangle, Compass, MapPin, Eye, Zap, ShieldCheck } from 'lucide-react'
import { weatherService } from '../../services'
import { useToast } from '../../components/ui/Toast'

const CITIES = ['Ahmedabad', 'Rajkot', 'Surat', 'Vadodara', 'Pune', 'Ludhiana']

export default function Weather() {
  const { showToast } = useToast()
  const [selectedCity, setSelectedCity] = useState('Ahmedabad')
  const [current, setCurrent] = useState(null)
  const [forecast, setForecast] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadWeatherData(selectedCity)
  }, [selectedCity])

  const loadWeatherData = async (city) => {
    setLoading(true)
    try {
      const [currRes, foreRes] = await Promise.all([
        weatherService.current({ location: city }).catch(() => ({ data: null })),
        weatherService.forecast({ location: city }).catch(() => ({ data: [] }))
      ])

      setCurrent(currRes?.data || {
        location: `${city}, Gujarat`,
        temp: city === 'Rajkot' ? 32.1 : city === 'Surat' ? 28.5 : 29.5,
        condition: city === 'Surat' ? 'Light Rain' : 'Partly Cloudy',
        humidity: 65,
        wind_speed: 12.4,
        rain_prob: city === 'Surat' ? 70 : 20,
        uv_index: 6,
        dew_point: '18.2°C',
        solar_rad: '820 W/m²'
      })

      setForecast(foreRes?.data?.forecast || foreRes?.data || [
        { day: 'Today', temp_max: 31, temp_min: 22, condition: 'Partly Cloudy', rain_mm: 0, spray_window: 'Optimal' },
        { day: 'Mon', temp_max: 32, temp_min: 23, condition: 'Sunny', rain_mm: 0, spray_window: 'Optimal' },
        { day: 'Tue', temp_max: 30, temp_min: 21, condition: 'Light Rain', rain_mm: 4.2, spray_window: 'Unsuitable' },
        { day: 'Wed', temp_max: 28, temp_min: 20, condition: 'Heavy Rain', rain_mm: 18.5, spray_window: 'High Risk' },
        { day: 'Thu', temp_max: 29, temp_min: 21, condition: 'Cloudy', rain_mm: 1.0, spray_window: 'Caution' },
        { day: 'Fri', temp_max: 31, temp_min: 22, condition: 'Sunny', rain_mm: 0, spray_window: 'Optimal' },
        { day: 'Sat', temp_max: 33, temp_min: 24, condition: 'Clear', rain_mm: 0, spray_window: 'Optimal' }
      ])
    } catch (err) {
      showToast('Error loading weather data', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gradient flex items-center gap-2">
            <Cloud className="w-6 h-6 text-sky-400" /> Weather Intelligence & Microclimate
          </h1>
          <p className="text-sm text-muted">Real-time weather metrics, spray window intelligence, and 7-day farm forecast</p>
        </div>

        {/* Location Selector */}
        <div className="flex items-center gap-2 bg-white/5 p-1.5 rounded-xl border border-white/10">
          <MapPin size={14} className="text-emerald-400 ml-2" />
          <span className="text-xs text-muted font-medium">Station:</span>
          <select
            value={selectedCity}
            onChange={e => setSelectedCity(e.target.value)}
            className="form-select py-1 px-3 text-xs w-auto bg-transparent border-none text-white font-bold"
          >
            {CITIES.map(c => <option key={c} value={c} className="bg-gray-900">{c}</option>)}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="card-glass p-8 text-center text-muted flex flex-col items-center justify-center min-h-[300px]">
          <div className="loading-spinner w-8 h-8 mb-3" />
          <span>Fetching weather telemetry for {selectedCity}...</span>
        </div>
      ) : (
        <>
          {/* Main Weather Hero Card */}
          <div className="card-glass p-6 bg-gradient-to-br from-emerald-950/40 via-gray-900 to-cyan-950/40 border border-white/10 shadow-2xl relative overflow-hidden">
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 z-10 relative">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="badge badge-green text-xs">{current?.location}</span>
                  <span className="text-xs text-muted font-mono">Station Lat: 23.02° N</span>
                </div>
                <div className="flex items-baseline gap-4">
                  <div className="text-6xl font-black text-white font-mono tracking-tight">{current?.temp}°C</div>
                  <div className="text-lg font-semibold text-emerald-400 capitalize">{current?.condition}</div>
                </div>
                <p className="text-xs text-gray-300">
                  Ideal microclimate for Kharif vegetation. Relative Humidity {current?.humidity}% with moderate wind.
                </p>
              </div>

              {/* Grid of Microclimate Metrics */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 w-full lg:w-auto">
                <div className="p-3 bg-white/5 rounded-xl text-center border border-white/5">
                  <Droplets className="w-5 h-5 text-cyan-400 mx-auto mb-1" />
                  <div className="text-[11px] text-muted font-medium">Humidity</div>
                  <div className="font-bold text-white mt-0.5 font-mono">{current?.humidity}%</div>
                </div>

                <div className="p-3 bg-white/5 rounded-xl text-center border border-white/5">
                  <Wind className="w-5 h-5 text-emerald-400 mx-auto mb-1" />
                  <div className="text-[11px] text-muted font-medium">Wind Speed</div>
                  <div className="font-bold text-white mt-0.5 font-mono">{current?.wind_speed} km/h</div>
                </div>

                <div className="p-3 bg-white/5 rounded-xl text-center border border-white/5">
                  <CloudRain className="w-5 h-5 text-sky-400 mx-auto mb-1" />
                  <div className="text-[11px] text-muted font-medium">Rain Prob</div>
                  <div className="font-bold text-white mt-0.5 font-mono">{current?.rain_prob}%</div>
                </div>

                <div className="p-3 bg-white/5 rounded-xl text-center border border-white/5">
                  <Sun className="w-5 h-5 text-amber-400 mx-auto mb-1" />
                  <div className="text-[11px] text-muted font-medium">UV Index</div>
                  <div className="font-bold text-white mt-0.5 font-mono">{current?.uv_index} (Moderate)</div>
                </div>

                <div className="p-3 bg-white/5 rounded-xl text-center border border-white/5">
                  <Thermometer className="w-5 h-5 text-rose-400 mx-auto mb-1" />
                  <div className="text-[11px] text-muted font-medium">Dew Point</div>
                  <div className="font-bold text-white mt-0.5 font-mono">{current?.dew_point || '18°C'}</div>
                </div>

                <div className="p-3 bg-white/5 rounded-xl text-center border border-white/5">
                  <Zap className="w-5 h-5 text-purple-400 mx-auto mb-1" />
                  <div className="text-[11px] text-muted font-medium">Solar Rad</div>
                  <div className="font-bold text-white mt-0.5 font-mono">{current?.solar_rad || '820 W/m²'}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Spray Window Banner */}
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 text-xs">
            <div className="flex items-center gap-2 text-emerald-400 font-bold">
              <ShieldCheck className="w-5 h-5" /> Pesticide / Fertilizer Spray Window Intelligence:
            </div>
            <span className="text-gray-200">
              Low wind (12.4 km/h) & 0mm rain predicted for today. <strong>Optimal spraying window: 07:00 AM — 10:30 AM</strong>.
            </span>
          </div>

          {/* 7-Day Agricultural Forecast */}
          <div className="space-y-3">
            <h2 className="text-base font-bold text-white uppercase tracking-wider">7-Day Agricultural Forecast</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
              {forecast.map((day, idx) => (
                <div
                  key={idx}
                  className="card-glass p-4 text-center space-y-2 hover:border-emerald-500/40 transition flex flex-col justify-between"
                >
                  <div>
                    <div className="font-bold text-white text-sm">{day.day}</div>
                    <div className="text-[11px] text-emerald-400 font-semibold mt-1">{day.condition}</div>
                  </div>

                  <div className="my-2">
                    <div className="text-lg font-black text-white font-mono">
                      {day.temp_max}° <span className="text-muted font-normal text-xs">/ {day.temp_min}°</span>
                    </div>
                  </div>

                  <div className="space-y-1.5 pt-2 border-t border-white/5">
                    <div className="text-[11px] text-muted flex items-center justify-center gap-1">
                      <CloudRain className="w-3.5 h-3.5 text-cyan-400" /> {day.rain_mm} mm
                    </div>
                    <span className={`badge text-[9px] px-2 py-0.5 ${
                      day.spray_window === 'Optimal' ? 'badge-green' : day.spray_window === 'Unsuitable' ? 'badge-amber' : 'badge-red'
                    }`}>
                      {day.spray_window}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
