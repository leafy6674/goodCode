import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { homeFor, useAuth } from '../AuthContext'

export default function Login() {
  const { user, login, register } = useAuth()
  const nav = useNavigate()
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ username: '', password: '', name: '', phone: '' })
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)

  if (user) return <Navigate to={homeFor(user.role)} replace />

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })
  const submit = async (e) => {
    e.preventDefault()
    setErr('')
    setBusy(true)
    try {
      const u = mode === 'login'
        ? await login(form.username, form.password)
        : await register({ ...form, phone: form.phone || null })
      nav(homeFor(u.role))
    } catch (ex) {
      setErr(ex.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-card card">
      <div className="tabs">
        <button className={mode === 'login' ? 'active' : ''} onClick={() => setMode('login')}>會員登入</button>
        <button className={mode === 'register' ? 'active' : ''} onClick={() => setMode('register')}>註冊會員</button>
      </div>
      <form onSubmit={submit}>
        <label>帳號<input value={form.username} onChange={set('username')} required autoFocus /></label>
        <label>密碼<input type="password" value={form.password} onChange={set('password')} required /></label>
        {mode === 'register' && (
          <>
            <label>姓名<input value={form.name} onChange={set('name')} required /></label>
            <label>手機 (選填)<input value={form.phone} onChange={set('phone')} /></label>
          </>
        )}
        {err && <div className="error">{err}</div>}
        <button className="primary" disabled={busy}>{mode === 'login' ? '登入' : '註冊並登入'}</button>
      </form>
      <div className="hint">
        示範帳號 (密碼皆為 <code>123456</code>)：<br />
        店長 <code>manager</code>、店員 <code>staff1</code>、會員 <code>member1</code>
      </div>
    </div>
  )
}
