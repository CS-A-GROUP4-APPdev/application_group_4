import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { HOME_BY_ROLE, currentUser, login } from '../auth.js'

export default function Login() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [remember, setRemember] = useState(false)
  const [errors, setErrors] = useState({})
  const [failure, setFailure] = useState('')
  const [busy, setBusy] = useState(false)

  const existing = currentUser()
  if (existing && HOME_BY_ROLE[existing.role]) return <Navigate to={HOME_BY_ROLE[existing.role]} replace />

  async function onSubmit(e) {
    e.preventDefault()
    setFailure('')
    const found = {}
    if (!username.trim()) found.username = 'Username is required.'
    if (!password) found.password = 'Password is required.'
    setErrors(found)
    if (Object.keys(found).length) return

    setBusy(true)
    try {
      const user = await login(username.trim(), password, remember)
      navigate(HOME_BY_ROLE[user.role] ?? '/dashboard', { replace: true })
    } catch (err) {
      setFailure(err.message)
      setBusy(false)
    }
  }

  return (
    <div className="login-split row g-0">
      {/* Left branding panel: desktop only */}
      <aside className="login-aside col-lg-6 d-none d-lg-flex flex-column justify-content-center px-5">
        <div className="logo-box lg d-flex mb-4">LOGO</div>
        <h1 className="login-headline mb-4">Know how your child is doing, not just the grade.</h1>
        <ul className="fs-5 ps-3">
          <li>Grades explained in plain language</li>
          <li>Attendance and reasons for absences</li>
          <li>Notices and meetings with teachers</li>
        </ul>
      </aside>

      <main className="col-lg-6 d-flex align-items-center justify-content-center p-4">
        <div className="login-box">
          {/* Mobile header: replaces the left panel */}
          <div className="text-center mb-4 d-lg-none">
            <div className="logo-box lg d-flex mx-auto mb-3">LOGO</div>
            <p className="h2 fw-bold mb-1">Gabay</p>
            <p className="text-muted mb-0">Know how your child is doing, not just the grade.</p>
          </div>

          <h2 className="h2 fw-bold mb-1">Log in</h2>
          <p className="text-muted d-none d-lg-block">Parents, teachers, and school staff sign in here.</p>

          {failure && <div className="alert alert-danger mt-3" role="alert">{failure}</div>}

          <form onSubmit={onSubmit} noValidate className="mt-3">
            <div className="mb-3">
              <label htmlFor="username" className="form-label fw-bold">Username</label>
              <input
                id="username" type="text" autoComplete="username"
                className={`form-control form-control-lg ${errors.username ? 'is-invalid' : ''}`}
                placeholder="Enter your username"
                value={username} onChange={(e) => setUsername(e.target.value)}
                aria-describedby={errors.username ? 'username-error' : undefined}
              />
              {errors.username && <div id="username-error" className="invalid-feedback">{errors.username}</div>}
            </div>

            <div className="mb-3">
              <label htmlFor="password" className="form-label fw-bold">Password</label>
              <input
                id="password" type="password" autoComplete="current-password"
                className={`form-control form-control-lg ${errors.password ? 'is-invalid' : ''}`}
                placeholder="Enter your password"
                value={password} onChange={(e) => setPassword(e.target.value)}
                aria-describedby={errors.password ? 'password-error' : undefined}
              />
              {errors.password && <div id="password-error" className="invalid-feedback">{errors.password}</div>}
            </div>

            <div className="form-check mb-3">
              <input id="remember" type="checkbox" className="form-check-input" checked={remember} onChange={(e) => setRemember(e.target.checked)} />
              <label htmlFor="remember" className="form-check-label">Remember me</label>
            </div>

            <button type="submit" className="btn btn-primary btn-lg w-100" disabled={busy}>
              {busy ? 'Logging in…' : 'Log in'}
            </button>
          </form>

          <p className="text-center text-muted small mt-4 mb-0">
            Forgot your password? Ask your adviser or the school office.
          </p>
        </div>
      </main>
    </div>
  )
}
