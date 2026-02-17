import { createContext, useContext, useState } from 'react'

type AuthCtx = { token: string | null; role: string | null; setAuth: (t: string | null, r: string | null) => void }
const Ctx = createContext<AuthCtx>({ token: null, role: null, setAuth: () => {} })

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [role, setRole] = useState<string | null>(localStorage.getItem('role'))
  const setAuth = (t: string | null, r: string | null) => {
    setToken(t); setRole(r)
    t ? localStorage.setItem('token', t) : localStorage.removeItem('token')
    r ? localStorage.setItem('role', r) : localStorage.removeItem('role')
  }
  return <Ctx.Provider value={{ token, role, setAuth }}>{children}</Ctx.Provider>
}

export const useAuth = () => useContext(Ctx)
