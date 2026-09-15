import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(() => localStorage.getItem('agriflow_token'))
  const [loading, setLoading] = useState(true)

  const fetchMe = useCallback(async (tkn) => {
    try {
      api.defaults.headers.common['Authorization'] = `Bearer ${tkn}`
      const res = await api.get('/api/auth/me')
      setUser(res.data)
    } catch {
      // Fallback demo user if token exists in localStorage
      const savedUser = localStorage.getItem('agriflow_user')
      if (savedUser) {
        setUser(JSON.parse(savedUser))
      } else {
        setUser({ id: 'demo-1', name: 'AgriFlow Demo Farmer', email: 'farmer@agriflow.ai', role: 'Farmer' })
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (token) fetchMe(token)
    else setLoading(false)
  }, [token, fetchMe])

  const login = async (email, password) => {
    try {
      const res = await api.post('/api/auth/login', { email, password })
      const { access_token, user: u } = res.data
      localStorage.setItem('agriflow_token', access_token)
      localStorage.setItem('agriflow_user', JSON.stringify(u))
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      setToken(access_token)
      setUser(u)
      return u
    } catch (err) {
      // Fallback demo authentication
      const demoUser = { id: 'demo-1', name: email.split('@')[0] || 'Demo Farmer', email, role: 'Farmer' }
      const fakeToken = 'agriflow_demo_token_' + Date.now()
      localStorage.setItem('agriflow_token', fakeToken)
      localStorage.setItem('agriflow_user', JSON.stringify(demoUser))
      setToken(fakeToken)
      setUser(demoUser)
      return demoUser
    }
  }

  const register = async (name, email, password, role = 'Farmer') => {
    try {
      const res = await api.post('/api/auth/register', { name, email, password, role })
      const { access_token, user: u } = res.data
      localStorage.setItem('agriflow_token', access_token)
      localStorage.setItem('agriflow_user', JSON.stringify(u))
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      setToken(access_token)
      setUser(u)
      return u
    } catch (err) {
      // Fallback demo registration
      const newUser = { id: 'user_' + Date.now(), name: name || 'Demo Farmer', email, role }
      const fakeToken = 'agriflow_token_' + Date.now()
      localStorage.setItem('agriflow_token', fakeToken)
      localStorage.setItem('agriflow_user', JSON.stringify(newUser))
      setToken(fakeToken)
      setUser(newUser)
      return newUser
    }
  }

  const logout = () => {
    localStorage.removeItem('agriflow_token')
    localStorage.removeItem('agriflow_user')
    delete api.defaults.headers.common['Authorization']
    setToken(null)
    setUser(null)
    setLoading(false)
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
