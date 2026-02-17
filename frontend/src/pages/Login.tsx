import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const [email, setEmail] = useState('admin@vp.local')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')
  const nav = useNavigate()
  const { setAuth } = useAuth()

  const submit = async (e: FormEvent) => {
    e.preventDefault(); setError('')
    try {
      const token = (await api.post('/auth/login', { email, password })).data.access_token
      localStorage.setItem('token', token)
      const me = (await api.get('/me')).data
      setAuth(token, me?.role || null)
      nav('/dashboard')
    } catch (err: any) {
      const detail = err?.response?.data?.detail
      if (typeof detail === "string") {
        setError(`Falha no login: ${detail}`)
      } else {
        setError("Falha no login. Verifique usuário e senha.")
      }
    } catch {
      setError('Falha no login. Verifique usuário e senha.')
    }
  }

  return <div className="login"><h1>Vigilância Patrimonial</h1><form onSubmit={submit}><input value={email} onChange={e=>setEmail(e.target.value)} /><input type="password" value={password} onChange={e=>setPassword(e.target.value)} /><button>Entrar</button>{error && <p>{error}</p>}</form></div>
}
