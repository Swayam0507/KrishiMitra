import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Eye, EyeOff, Mail, Lock, User, Sprout } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { useToast } from '../../components/ui/Toast'

export default function Login() {
  const { login } = useAuth()
  const { toast } = useToast ? { toast: useToast() } : { toast: { error: alert } }
  const toastObj = useToast()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [show, setShow] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(form.email, form.password)
      toastObj.success('Welcome back to AgriFlow AI!')
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      {/* Left panel */}
      <div className="auth-left">
        <div style={{ maxWidth: 480, width: '100%' }}>
          <div className="auth-logo" style={{ justifyContent: 'center', marginBottom: 48 }}>
            <div className="auth-logo-icon">🌾</div>
            <div>
              <h1 className="auth-title">AgriFlow AI</h1>
              <p style={{ color: 'var(--accent-green)', fontSize: 13, fontWeight: 600 }}>
                Intelligent Farm Management
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {[
              { icon: '🔬', title: 'AI Disease Detection', desc: 'Computer vision powered crop health analysis' },
              { icon: '🌱', title: 'Smart Crop Recommendation', desc: 'ML-based crop selection for your soil' },
              { icon: '💧', title: 'Irrigation Intelligence', desc: 'Save water with smart irrigation decisions' },
              { icon: '🤖', title: 'Agentic Farm Advisor', desc: 'Autonomous advisory workflow for your farm' },
            ].map(f => (
              <div key={f.title} className="auth-feature">
                <div className="auth-feature-icon" style={{ background: 'rgba(34,197,94,0.1)' }}>{f.icon}</div>
                <div className="auth-feature-text">
                  <h4>{f.title}</h4>
                  <p>{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right panel */}
      <div className="auth-right">
        <div style={{ width: '100%', maxWidth: 380 }}>
          <h2 style={{ fontSize: 26, fontWeight: 800, marginBottom: 8 }}>Welcome back</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginBottom: 32 }}>
            Sign in to your AgriFlow AI account
          </p>

          <form className="auth-form" onSubmit={handleSubmit}>
            {error && (
              <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 8, padding: '12px 14px', color: 'var(--accent-red)', fontSize: 13 }}>
                {error}
              </div>
            )}

            <div className="form-group">
              <label className="form-label">Email</label>
              <div className="input-group">
                <Mail className="input-group-icon" size={16} />
                <input
                  id="login-email"
                  type="email"
                  className="form-input"
                  placeholder="you@example.com"
                  value={form.email}
                  onChange={e => setForm(p => ({ ...p, email: e.target.value }))}
                  required
                  autoFocus
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Password</label>
              <div className="input-group">
                <Lock className="input-group-icon" size={16} />
                <input
                  id="login-password"
                  type={show ? 'text' : 'password'}
                  className="form-input"
                  placeholder="••••••••"
                  style={{ paddingRight: 44 }}
                  value={form.password}
                  onChange={e => setForm(p => ({ ...p, password: e.target.value }))}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShow(!show)}
                  style={{ position: 'absolute', right: 12, background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', display: 'flex' }}
                >
                  {show ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button id="login-submit" type="submit" className="btn btn-primary w-full btn-lg" disabled={loading}>
              {loading ? <><span className="loading-spinner" style={{ width: 18, height: 18 }} /> Signing in...</> : 'Sign In'}
            </button>

            <p style={{ textAlign: 'center', fontSize: 14, color: 'var(--text-secondary)' }}>
              Don't have an account?{' '}
              <Link to="/register" style={{ color: 'var(--accent-green)', fontWeight: 600 }}>Create account</Link>
            </p>
          </form>

          {/* Demo hint */}
          <div style={{ marginTop: 24, padding: '12px 16px', background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', borderRadius: 8, fontSize: 12, color: 'var(--accent-amber)' }}>
            <strong>Demo:</strong> Register a new account to explore all features.
          </div>
        </div>
      </div>
    </div>
  )
}
