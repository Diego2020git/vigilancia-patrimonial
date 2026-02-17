import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function Dashboard() {
  const [finance, setFinance] = useState<any>({})
  const [ops, setOps] = useState<any>({})
  useEffect(() => { api.get('/dashboard/finance').then(r=>setFinance(r.data)).catch(()=>{}); api.get('/dashboard/operations').then(r=>setOps(r.data)).catch(()=>{}) }, [])
  return <div><h2>Dashboard</h2><div className="cards"><article>Pagos: {finance.paid ?? '-'}</article><article>Pendentes: {finance.pending ?? '-'}</article><article>Atrasados: {finance.late ?? '-'}</article><article>Rondas: {ops.rounds_period ?? '-'}</article><article>Tickets abertos: {ops.tickets_open ?? '-'}</article><article>Coberturas pendentes: {ops.coverages_pending ?? '-'}</article></div></div>
}
