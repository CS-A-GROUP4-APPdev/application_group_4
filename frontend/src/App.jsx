import { Navigate, Route, Routes } from 'react-router-dom'
import { currentUser } from './auth.js'
import Login from './pages/Login.jsx'
import ParentDashboard from './pages/ParentDashboard.jsx'

// Anyone who is not logged in is sent back to the login page.
function RequireLogin({ children }) {
  return currentUser() ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={<RequireLogin><ParentDashboard /></RequireLogin>} />
      {/* Any unknown address goes back to the login page for now */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}
