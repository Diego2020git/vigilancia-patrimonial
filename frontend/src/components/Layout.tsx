import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Layout({ children }: { children: React.ReactNode }) {
  const { role, setAuth } = useAuth()
  const links = role === 'admin'
    ? ['Dashboard','Unidades','Moradores','Funcionários','Financeiro','Agenda','Coberturas','Tickets','Rondas','Configurações','Auditoria']
    : role === 'funcionario' ? ['Minhas Coberturas','Tickets','Rondas'] : ['Minha Unidade','Pagamentos','Agenda','Tickets']

  return <div className="app"><aside>{links.map(l => <Link key={l} to={`/${l.toLowerCase().split(' ').join('-')}`}>{l}</Link>)}<button onClick={()=>setAuth(null,null)}>Sair</button></aside><main>{children}</main></div>
}
