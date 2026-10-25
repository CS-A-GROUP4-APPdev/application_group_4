// Static login layout only. No backend connection yet:
// the form does not send anything when submitted.
export default function Login() {
  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center p-3">
      <div className="card shadow-sm login-card">
        <div className="card-body p-4">
          <h1 className="h3 text-center mb-1">Gabay</h1>
          <p className="text-center text-muted mb-4">
            Student Progress and Attendance Monitoring
          </p>

          <form onSubmit={(e) => e.preventDefault()}>
            <div className="mb-3">
              <label htmlFor="username" className="form-label">Username</label>
              <input
                id="username"
                type="text"
                className="form-control"
                placeholder="Enter your username"
                autoComplete="username"
              />
            </div>

            <div className="mb-3">
              <label htmlFor="password" className="form-label">Password</label>
              <input
                id="password"
                type="password"
                className="form-control"
                placeholder="Enter your password"
                autoComplete="current-password"
              />
            </div>

            <div className="form-check mb-3">
              <input id="remember" type="checkbox" className="form-check-input" />
              <label htmlFor="remember" className="form-check-label">Remember me</label>
            </div>

            <button type="submit" className="btn btn-primary w-100">Log in</button>
          </form>

          <p className="text-center text-muted small mt-4 mb-0">
            Parents, teachers, and school staff sign in here.
          </p>
        </div>
      </div>
    </div>
  )
}
