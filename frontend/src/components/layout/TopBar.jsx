import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { Bell, RefreshCw, Menu } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { useLanguage } from '../../context/LanguageContext'
import { alertService } from '../../services'

const PAGE_TITLES = {
  '/dashboard':      { title: 'Dashboard',          sub: 'Your farm at a glance' },
  '/farms':          { title: 'My Farms',            sub: 'Manage your farms' },
  '/plots':          { title: 'Plots',               sub: 'Field management' },
  '/crops':          { title: 'Crops',               sub: 'Active crop cycles' },
  '/activities':     { title: 'Activities',          sub: 'Farm task schedule' },
  '/workers':        { title: 'Workers',             sub: 'Labour management' },
  '/expenses':       { title: 'Expenses',            sub: 'Financial tracking' },
  '/inventory':      { title: 'Inventory',           sub: 'Stock management' },
  '/disease':        { title: 'Disease Detection',   sub: 'AI crop health analysis' },
  '/recommendation': { title: 'Crop Recommendation', sub: 'AI-powered crop selection' },
  '/irrigation':     { title: 'Smart Irrigation',    sub: 'Water intelligence' },
  '/weather':        { title: 'Weather',             sub: 'Agricultural weather intelligence' },
  '/sensors':        { title: 'IoT Sensors',         sub: 'Simulated sensor data' },
  '/advisor':        { title: 'Agentic Advisor',     sub: 'AI farm decision workflow' },
  '/assistant':      { title: 'AI Assistant',        sub: 'Grounded farm assistant' },
  '/intelligence':   { title: 'Intelligence Loop',   sub: 'AI decision cycle visualization' },
  '/alerts':         { title: 'Alerts',              sub: 'Notification center' },
  '/analytics':      { title: 'Analytics',           sub: 'Farm performance metrics' },
  '/reports':        { title: 'Reports',             sub: 'Export and reporting' },
  '/map':            { title: 'Farm Map',            sub: 'Visual farm layout' },
}

export default function TopBar() {
  const { pathname } = useLocation()
  const { lang, setLanguage } = useLanguage()
  const { user } = useAuth()
  const [alertCount, setAlertCount] = useState(0)

  const pageKey = Object.keys(PAGE_TITLES).find(k => pathname.startsWith(k)) || '/dashboard'
  const page = PAGE_TITLES[pageKey]

  useEffect(() => {
    alertService.summary().then(r => setAlertCount(r.data.total || 0)).catch(() => {})
  }, [pathname])

  return (
    <header className="topbar">
      <div className="topbar-left">
        <div>
          <div className="topbar-title">{page.title}</div>
          <div className="topbar-subtitle">{page.sub}</div>
        </div>
      </div>

      <div className="topbar-right">
        {/* Language selector */}
        <select
          className="lang-select"
          value={lang}
          onChange={e => setLanguage(e.target.value)}
          title="Switch language"
        >
          <option value="en">🇬🇧 EN</option>
          <option value="hi">🇮🇳 हिं</option>
          <option value="gu">🇮🇳 ગુ</option>
        </select>

        {/* Alerts */}
        <a href="/alerts" className="topbar-btn" title="Alerts">
          <Bell size={17} />
          {alertCount > 0 && <span className="topbar-badge">{alertCount > 9 ? '9+' : alertCount}</span>}
        </a>
      </div>
    </header>
  )
}
