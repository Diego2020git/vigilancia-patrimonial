import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { api } from './api/client'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import ListPage from './pages/ListPage'
import Layout from './components/Layout'
import { useAuth } from './context/AuthContext'

function Private({ children }: { children: JSX.Element }) {
  const { token } = useAuth()
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  const [brand, setBrand] = useState<any>({ brand_name: 'Vigilância Patrimonial', primary_color: '#14b8a6', secondary_color: '#111827', logo_path: '/logo.svg' })
  const loc = useLocation()
  useEffect(() => { api.get('/public-config').then(r => setBrand(r.data)).catch(() => {}) }, [])
  useEffect(() => {
    document.documentElement.style.setProperty('--primary', brand.primary_color)
    document.documentElement.style.setProperty('--secondary', brand.secondary_color)
  }, [brand])

  return <>
    {loc.pathname !== '/login' && <header><img src={`http://localhost:8000${brand.logo_path}`} height={32} /><strong>{brand.brand_name}</strong></header>}
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/*" element={<Private><Layout><Routes>
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="unidades" element={<ListPage title="Unidades" endpoint="/units" />} />
        <Route path="moradores" element={<ListPage title="Moradores" endpoint="/users" />} />
        <Route path="funcionários" element={<ListPage title="Funcionários" endpoint="/users" />} />
        <Route path="financeiro" element={<ListPage title="Financeiro" endpoint="/payments" />} />
        <Route path="agenda" element={<ListPage title="Agenda" endpoint="/agenda" />} />
        <Route path="coberturas" element={<ListPage title="Coberturas" endpoint="/coverages" />} />
        <Route path="tickets" element={<ListPage title="Tickets" endpoint="/tickets" />} />
        <Route path="rondas" element={<ListPage title="Rondas" endpoint="/rounds" />} />
        <Route path="configurações" element={<ListPage title="Configurações" endpoint="/public-config" />} />
        <Route path="auditoria" element={<ListPage title="Auditoria" endpoint="/audit" />} />
        <Route path="minhas-coberturas" element={<ListPage title="Minhas Coberturas" endpoint="/coverages" />} />
        <Route path="minha-unidade" element={<ListPage title="Minha Unidade" endpoint="/units" />} />
        <Route path="pagamentos" element={<ListPage title="Pagamentos" endpoint="/payments" />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes></Layout></Private>} />
    </Routes>
  </>
}
