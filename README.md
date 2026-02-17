# Sistema WEB de Gestão de Vigilância Patrimonial

Projeto completo com **backend FastAPI** e **frontend React + Vite + TypeScript**, preparado para rodar localmente no **Windows sem Docker**.

## Estrutura

- `backend/` API REST (FastAPI + SQLModel + SQLite `app.db`)
- `frontend/` aplicação web (React + Vite + TypeScript)
- `scripts/` scripts `.bat` para iniciar no Windows

## Requisitos

- Python 3.11+
- Node.js 18+
- npm

## Subir backend (Windows)

```bat
cd backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger: `http://localhost:8000/docs`

## Subir frontend (Windows)

```bat
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`

## Usuários demo (seed automático)

- Admin: `admin@vp.local` / `admin123`
- Funcionário: `func@vp.local` / `func123`
- Morador: `morador@vp.local` / `morador123`

## Funcionalidades entregues

- JWT com senha em bcrypt
- RBAC (Admin, Funcionário, Morador)
- Agenda com bloqueio configurável e detecção de conflito por unidade
- Tipos com aprovação (`mudanca`, `prestador`, `visita` em horário bloqueado)
- Tipo `saida` gera cobertura automática
- Rondas com múltiplas fotos e metadados de upload
- Auditoria completa de eventos
- Dashboard financeiro e operacional
- Configuração pública de marca em `/public-config`
- Upload de logo por admin
- CORS liberado para `http://localhost:5173`

## Scripts rápidos (Windows)

- `scripts\start_backend_windows.bat`
- `scripts\start_frontend_windows.bat`


## Solução rápida para erro `email-validator`

Se aparecer `ImportError: email-validator is not installed`, rode o script atualizado de backend:

```bat
.\scripts\start_backend_windows.bat
```

Esse script valida o ambiente e força a instalação de `pydantic[email]` se o `email_validator` não estiver disponível.
