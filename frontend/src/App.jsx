import { Navigate, Route, Routes } from 'react-router-dom'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={<Dashboard />} />
      {/* Any unknown address goes back to the login page for now */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}
