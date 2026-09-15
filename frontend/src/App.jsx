import React, { useState, useCallback } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import { LanguageProvider } from './context/LanguageContext'
import { ToastProvider } from './components/ui/Toast'
import MainLayout from './layouts/MainLayout'

// Auth Pages
import Login    from './pages/auth/Login'
import Register from './pages/auth/Register'

// Core Pages
import Dashboard         from './pages/Dashboard'
import FarmList          from './pages/farms/FarmList'
import FarmDetail        from './pages/farms/FarmDetail'
import PlotList          from './pages/plots/PlotList'
import CropList          from './pages/crops/CropList'
import CropDetail        from './pages/crops/CropDetail'
import ActivityList      from './pages/activities/ActivityList'
import WorkerList        from './pages/workers/WorkerList'
import ExpenseList       from './pages/expenses/ExpenseList'
import InventoryList     from './pages/inventory/InventoryList'

// AI Pages
import DiseaseDetection  from './pages/disease/DiseaseDetection'
import CropRecommendation from './pages/recommendation/CropRecommendation'
import IrrigationAdvisor  from './pages/irrigation/IrrigationAdvisor'
import Weather           from './pages/weather/Weather'
import AgentAdvisor      from './pages/advisor/AgentAdvisor'
import Assistant         from './pages/assistant/Assistant'
import AlertCenter       from './pages/alerts/AlertCenter'
import Analytics         from './pages/analytics/Analytics'
import Reports           from './pages/reports/Reports'
import IntelligenceLoop  from './pages/IntelligenceLoop'
import FarmMap           from './pages/FarmMap'

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-primary)' }}>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
        <div className="loading-spinner" style={{ width: 40, height: 40 }} />
        <span style={{ color: 'var(--text-muted)', fontSize: 14 }}>Loading AgriFlow AI...</span>
      </div>
    </div>
  )
  return isAuthenticated ? children : <Navigate to="/login" replace />
}

function PublicRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  if (loading) return null
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : children
}

export default function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <ToastProvider>
          <BrowserRouter>
            <Routes>
              {/* Public */}
              <Route path="/login"    element={<PublicRoute><Login /></PublicRoute>} />
              <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

              {/* Protected */}
              <Route path="/" element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard"      element={<Dashboard />} />
                <Route path="farms"          element={<FarmList />} />
                <Route path="farms/:id"      element={<FarmDetail />} />
                <Route path="plots"          element={<PlotList />} />
                <Route path="crops"          element={<CropList />} />
                <Route path="crops/:id"      element={<CropDetail />} />
                <Route path="activities"     element={<ActivityList />} />
                <Route path="workers"        element={<WorkerList />} />
                <Route path="expenses"       element={<ExpenseList />} />
                <Route path="inventory"      element={<InventoryList />} />
                <Route path="disease"        element={<DiseaseDetection />} />
                <Route path="recommendation" element={<CropRecommendation />} />
                <Route path="irrigation"     element={<IrrigationAdvisor />} />
                <Route path="weather"        element={<Weather />} />
                <Route path="advisor"        element={<AgentAdvisor />} />
                <Route path="assistant"      element={<Assistant />} />
                <Route path="alerts"         element={<AlertCenter />} />
                <Route path="analytics"      element={<Analytics />} />
                <Route path="reports"        element={<Reports />} />
                <Route path="intelligence"   element={<IntelligenceLoop />} />
                <Route path="map"            element={<FarmMap />} />
              </Route>

              {/* 404 */}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </BrowserRouter>
        </ToastProvider>
      </AuthProvider>
    </LanguageProvider>
  )
}
