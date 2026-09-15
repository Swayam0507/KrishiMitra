import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Eye, EyeOff, Mail, Lock, User } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { useToast } from '../../components/ui/Toast'

export default function Register() {
  const { register } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'Farmer' })
  const [show, setShow] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (form.password.length < 6) { setError('Password must be at least 6 characters.'); return }
    setLoading(true)
    try {
      await register(form.name, form.email, form.password, form.role)
      toast.success('Account created! Welcome to AgriFlow AI.')
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-left">
        <div style={{ maxWidth: 480, width: '100%', textAlign: 'center' }}>
          <div style={{ fontSize: 80, marginBottom: 24 }}>🌾</div>
          <h1 style={{ fontSize: 36, fontWeight: 800, marginBottom: 12, letterSpacing: '-0.03em' }}>
            AgriFlow AI
          </h1>
          <p style={{ fontSize: 18, color: 'var(--text-secondary)', lineHeight: 1.6, maxWidth: 380, margin: '0 auto' }}>
            Intelligent Farm Management powered by Computer Vision, Machine Learning, and Agentic AI
          </p>
          <div style={{ marginTop: 40, display: 'flex', gap: 12, flexWrap: 'wrap', justifyContent: 'center' }}>
            {['Disease AI', 'Crop ML', 'Smart Irrigation', 'Weather', 'IoT Sensors', 'GenAI Assistant', 'Sustainability'].map(tag => (
              <span key={tag} className="badge badge-green">{tag}</span>
            ))}
          </div>
        </div>
      </div>

      <div className="auth-right">
        <div style={{ width: '100%', maxWidth: 380 }}>
          <h2 style={{ fontSize: 26, fontWeight: 800, marginBottom: 8 }}>Create account</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginBottom: 32 }}>
            Start managing your farm intelligently
          </p>

          <form className="auth-form" onSubmit={handleSubmit}>
            {error && (
              <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 8, padding: '12px 14px', color: 'var(--accent-red)', fontSize: 13 }}>
                {error}
              </div>
            )}

            <div className="form-group">
              <label className="form-label">Full Name</label>
              <div className="input-group">
                <User className="input-group-icon" size={16} />
                <input id="reg-name" type="text" className="form-input" placeholder="Rajesh Patel"
                  value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} required autoFocus />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Email</label>
              <div className="input-group">
                <Mail className="input-group-icon" size={16} />
                <input id="reg-email" type="email" className="form-input" placeholder="you@example.com"
                  value={form.email} onChange={e => setForm(p => ({ ...p, email: e.target.value }))} required />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Role</label>
              <select id="reg-role" className="form-select" value={form.role}
                onChange={e => setForm(p => ({ ...p, role: e.target.value }))}>
                <option value="Farmer">Farmer</option>
                <option value="Agronomist">Agronomist</option>
                <option value="Manager">Farm Manager</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Password</label>
              <div className="input-group">
                <Lock className="input-group-icon" size={16} />
                <input id="reg-password" type={show ? 'text' : 'password'} className="form-input"
                  placeholder="Min. 6 characters" style={{ paddingRight: 44 }}
                  value={form.password} onChange={e => setForm(p => ({ ...p, password: e.target.value }))} required />
                <button type="button" onClick={() => setShow(!show)}
                  style={{ position: 'absolute', right: 12, background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', display: 'flex' }}>
                  {show ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button id="reg-submit" type="submit" className="btn btn-primary w-full btn-lg" disabled={loading}>
              {loading ? <><span className="loading-spinner" style={{ width: 18, height: 18 }} /> Creating account...</> : 'Create Account'}
            </button>

            <p style={{ textAlign: 'center', fontSize: 14, color: 'var(--text-secondary)' }}>
              Already have an account?{' '}
              <Link to="/login" style={{ color: 'var(--accent-green)', fontWeight: 600 }}>Sign in</Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  )
}
