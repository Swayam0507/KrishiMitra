import React, { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Sprout, Map, Wheat, ClipboardList,
  Users, Wallet, Package, Microscope, FlaskConical,
  Droplets, Cloud, Bot, MessageSquare, AlertCircle,
  BarChart2, FileText, Cpu, Brain, LogOut, Menu, X, Activity
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { useLanguage } from '../../context/LanguageContext'

const NAV_ITEMS = [
  { section: 'Main', items: [
    { path: '/dashboard',   icon: LayoutDashboard, key: 'dashboard' },
    { path: '/map',         icon: Map,             key: 'farms', label: 'Farm Map' },
    { path: '/farms',       icon: Sprout,          key: 'farms' },
    { path: '/plots',       icon: Map,             key: 'plots' },
    { path: '/crops',       icon: Wheat,           key: 'crops' },
  ]},
  { section: 'Operations', items: [
    { path: '/activities',  icon: ClipboardList,   key: 'activities' },
    { path: '/workers',     icon: Users,           key: 'workers' },
    { path: '/expenses',    icon: Wallet,          key: 'expenses' },
    { path: '/inventory',   icon: Package,         key: 'inventory' },
  ]},
  { section: 'AI & Analytics', items: [
    { path: '/disease',        icon: Microscope,     key: 'disease' },
    { path: '/recommendation', icon: FlaskConical,   key: 'recommendation' },
    { path: '/irrigation',     icon: Droplets,       key: 'irrigation' },
    { path: '/weather',        icon: Cloud,          key: 'weather' },
    { path: '/advisor',        icon: Bot,            key: 'advisor' },
    { path: '/assistant',      icon: MessageSquare,  key: 'assistant' },
    { path: '/intelligence',   icon: Brain,          key: 'advisor', label: 'Intelligence Loop' },
  ]},
  { section: 'Reports', items: [
    { path: '/alerts',     icon: AlertCircle, key: 'alerts' },
    { path: '/analytics',  icon: BarChart2,   key: 'analytics' },
    { path: '/reports',    icon: FileText,    key: 'reports' },
  ]},
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const { t } = useLanguage()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">🌾</div>
        <div className="sidebar-logo-text">
          <h2>AgriFlow AI</h2>
          <span>Farm Intelligence</span>
        </div>
      </div>

      {/* Nav Items */}
      <div style={{ flex: 1, paddingTop: 8 }}>
        {NAV_ITEMS.map(section => (
          <div key={section.section} className="sidebar-section">
            <div className="sidebar-section-label">{section.section}</div>
            {section.items.map(item => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
              >
                <item.icon className="sidebar-link-icon" size={17} />
                {item.label || t('nav', item.key)}
              </NavLink>
            ))}
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="sidebar-avatar">
            {user?.name?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="sidebar-user-info">
            <div className="sidebar-user-name truncate">{user?.name || 'User'}</div>
            <div className="sidebar-user-role">{user?.role || 'Farmer'}</div>
          </div>
          <button onClick={handleLogout} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', padding: 4, borderRadius: 6, display: 'flex' }}
            title="Logout">
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </nav>
  )
}
