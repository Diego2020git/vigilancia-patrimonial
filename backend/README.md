# Backend - Vigilância Patrimonial

## Stack

- FastAPI
- SQLModel
- SQLite (`app.db`)
- JWT + bcrypt

## Executar

```bat
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints principais

- `POST /auth/login`
- `GET /public-config`
- `PUT /admin/public-config`
- `POST /admin/public-config/logo`
- `CRUD`: usuários, unidades, pagamentos, agenda, tickets, rondas, coberturas
- `GET /dashboard/finance`
- `GET /dashboard/operations`
- `GET /audit`

Documentação interativa: `/docs`
