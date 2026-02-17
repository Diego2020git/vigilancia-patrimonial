import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function ListPage({ title, endpoint }: { title: string; endpoint: string }) {
  const [data, setData] = useState<any[]>([])
  useEffect(() => { api.get(endpoint).then(r=>setData(r.data)).catch(()=>setData([])) }, [endpoint])
  return <div><h2>{title}</h2><pre>{JSON.stringify(data, null, 2)}</pre></div>
}
