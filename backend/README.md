# Backend - Vigilância Patrimonial

## Stack

- FastAPI
- SQLModel
- SQLite (`app.db`)
- JWT + bcrypt

## Executar

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
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
