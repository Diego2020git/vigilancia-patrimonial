from pathlib import Path
from uuid import uuid4
from fastapi import Depends, FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select, func
from .config import settings
from .db import create_db_and_tables, get_session, engine
from .models import *
from .schemas import *
from .auth import create_access_token, verify_password, hash_password, get_current_user, require_roles
from .seed import seed_data
from .services import add_audit, has_overlap, in_lock_window

app = FastAPI(title="Vigilância Patrimonial API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE = Path(__file__).resolve().parents[1]
storage = BASE / "storage"
public = BASE / "public"
storage.mkdir(exist_ok=True)
public.mkdir(exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(storage)), name="storage")
app.mount("/public", StaticFiles(directory=str(public)), name="public")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    with Session(engine) as s:
        seed_data(s)


@app.post("/auth/login", response_model=TokenResponse)
def login(data: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == data.email)).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Credenciais inválidas")
    token = create_access_token(user.email)
    add_audit(session, user.id, "login", "auth", user.id)
    return TokenResponse(access_token=token)


@app.get("/public-config")
def get_public_config(session: Session = Depends(get_session)):
    cfg = session.exec(select(PublicConfig)).first()
    return cfg


@app.put("/admin/public-config")
def update_public_config(data: PublicConfigUpdate, user: User = Depends(require_roles(Role.admin)), session: Session = Depends(get_session)):
    cfg = session.exec(select(PublicConfig)).first()
    cfg.brand_name, cfg.primary_color, cfg.secondary_color = data.brand_name, data.primary_color, data.secondary_color
    session.add(cfg)
    session.commit()
    add_audit(session, user.id, "update", "public_config", cfg.id)
    return cfg


@app.post("/admin/public-config/logo")
def upload_logo(file: UploadFile = File(...), user: User = Depends(require_roles(Role.admin)), session: Session = Depends(get_session)):
    ext = Path(file.filename).suffix or ".svg"
    rel = f"logo{ext}"
    target = public / rel
    target.write_bytes(file.file.read())
    cfg = session.exec(select(PublicConfig)).first()
    cfg.logo_path = f"/public/{rel}"
    session.add(cfg)
    session.commit()
    add_audit(session, user.id, "upload", "logo", cfg.id)
    return {"logo_path": cfg.logo_path}




@app.get("/me")
def me(user: User = Depends(get_current_user)):
    return user

@app.post("/users", response_model=UserOut)
def create_user(data: UserCreate, user: User = Depends(require_roles(Role.admin)), session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.email == data.email)).first():
        raise HTTPException(400, "E-mail já cadastrado")
    db_u = User(name=data.name, email=data.email, password_hash=hash_password(data.password), role=data.role, unit_id=data.unit_id)
    session.add(db_u)
    session.commit(); session.refresh(db_u)
    add_audit(session, user.id, "create", "user", db_u.id)
    return UserOut(id=db_u.id, name=db_u.name, email=db_u.email, role=db_u.role, unit_id=db_u.unit_id)


@app.get("/users")
def list_users(user: User = Depends(require_roles(Role.admin)), session: Session = Depends(get_session)):
    return session.exec(select(User)).all()


@app.post("/units")
def create_unit(data: UnitCreate, user: User = Depends(require_roles(Role.admin)), session: Session = Depends(get_session)):
    unit = Unit(**data.model_dump())
    session.add(unit); session.commit(); session.refresh(unit)
    add_audit(session, user.id, "create", "unit", unit.id)
    return unit


@app.get("/units")
def list_units(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    if user.role == Role.morador and user.unit_id:
        return [session.get(Unit, user.unit_id)]
    return session.exec(select(Unit)).all()


@app.post("/payments")
def create_payment(data: PaymentCreate, user: User = Depends(require_roles(Role.admin)), session: Session = Depends(get_session)):
    p = Payment(**data.model_dump())
    session.add(p); session.commit(); session.refresh(p)
    add_audit(session, user.id, "create", "payment", p.id)
    return p


@app.get("/payments")
def list_payments(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    q = select(Payment)
    if user.role == Role.morador:
        q = q.where(Payment.unit_id == user.unit_id)
    return session.exec(q).all()


@app.post("/agenda")
def create_agenda(data: AgendaCreate, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    if user.role == Role.morador and user.unit_id != data.unit_id:
        raise HTTPException(403, "Morador só pode criar agenda da própria unidade")
    if data.end_at <= data.start_at:
        raise HTTPException(400, "Data final deve ser posterior à inicial")
    if has_overlap(session, data.unit_id, data.start_at, data.end_at):
        raise HTTPException(400, "Conflito de agenda para a unidade (interval overlap)")

    lock = session.exec(select(LockWindow).where(LockWindow.enabled == True)).first()
    blocked = lock and in_lock_window(data.start_at, data.end_at, lock)
    requires = data.type in [AgendaType.mudanca, AgendaType.prestador] or (data.type == AgendaType.visita and blocked)
    status = AgendaStatus.pendente if requires else AgendaStatus.aprovado

    ag = Agenda(**data.model_dump(), requester_id=user.id, requires_approval=bool(requires), status=status)
    session.add(ag); session.commit(); session.refresh(ag)
    add_audit(session, user.id, "create", "agenda", ag.id)

    if data.type == AgendaType.saida:
        cov = Coverage(unit_id=ag.unit_id, from_agenda_id=ag.id, title=f"Cobertura automática da saída #{ag.id}")
        session.add(cov); session.commit(); add_audit(session, user.id, "create", "coverage", cov.id, "Gerada automaticamente por saída")

    return ag


@app.get("/agenda")
def list_agenda(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    q = select(Agenda)
    if user.role == Role.morador:
        q = q.where(Agenda.unit_id == user.unit_id)
    return session.exec(q).all()


@app.patch("/agenda/{agenda_id}/approve")
def approve_agenda(agenda_id: int, data: AgendaApprove, user: User = Depends(require_roles(Role.admin)), session: Session = Depends(get_session)):
    ag = session.get(Agenda, agenda_id)
    if not ag:
        raise HTTPException(404, "Agenda não encontrada")
    ag.status = data.status
    session.add(ag); session.commit()
    add_audit(session, user.id, "approve", "agenda", agenda_id, data.status)
    return ag


@app.get("/coverages")
def list_coverages(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    q = select(Coverage)
    if user.role == Role.funcionario:
        q = q.where(Coverage.assigned_to == user.id)
    if user.role == Role.morador:
        q = q.where(Coverage.unit_id == user.unit_id)
    return session.exec(q).all()


@app.patch("/coverages/{coverage_id}")
def assign_coverage(coverage_id: int, data: CoverageAssign, user: User = Depends(require_roles(Role.admin, Role.funcionario)), session: Session = Depends(get_session)):
    c = session.get(Coverage, coverage_id)
    if not c:
        raise HTTPException(404, "Cobertura não encontrada")
    c.assigned_to = data.assigned_to
    c.status = data.status
    session.add(c); session.commit()
    add_audit(session, user.id, "update", "coverage", c.id)
    return c


@app.post("/tickets")
def create_ticket(data: TicketCreate, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    if user.role == Role.morador and user.unit_id != data.unit_id:
        raise HTTPException(403, "Morador só pode abrir ticket da própria unidade")
    t = Ticket(unit_id=data.unit_id, opened_by=user.id, title=data.title, description=data.description)
    session.add(t); session.commit(); session.refresh(t)
    add_audit(session, user.id, "create", "ticket", t.id)
    return t


@app.get("/tickets")
def list_tickets(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    q = select(Ticket)
    if user.role == Role.funcionario:
        q = q.where((Ticket.assigned_to == user.id) | (Ticket.assigned_to == None))
    if user.role == Role.morador:
        q = q.where(Ticket.unit_id == user.unit_id)
    return session.exec(q).all()


@app.patch("/tickets/{ticket_id}")
def update_ticket(ticket_id: int, data: TicketUpdate, user: User = Depends(require_roles(Role.admin, Role.funcionario)), session: Session = Depends(get_session)):
    t = session.get(Ticket, ticket_id)
    if not t:
        raise HTTPException(404, "Ticket não encontrado")
    t.status = data.status
    if data.assigned_to is not None:
        t.assigned_to = data.assigned_to
    session.add(t); session.commit()
    add_audit(session, user.id, "update", "ticket", t.id)
    return t


@app.post("/rounds")
def create_round(data: RoundCreate, user: User = Depends(require_roles(Role.admin, Role.funcionario)), session: Session = Depends(get_session)):
    employee_id = user.id if user.role == Role.funcionario else user.id
    r = Round(unit_id=data.unit_id, employee_id=employee_id, location=data.location, happened_at=data.happened_at, observation=data.observation)
    session.add(r); session.commit(); session.refresh(r)
    add_audit(session, user.id, "create", "round", r.id)
    return r


@app.post("/rounds/{round_id}/photos")
def upload_round_photo(round_id: int, files: list[UploadFile] = File(...), user: User = Depends(require_roles(Role.admin, Role.funcionario)), session: Session = Depends(get_session)):
    r = session.get(Round, round_id)
    if not r:
        raise HTTPException(404, "Ronda não encontrada")
    saved = []
    for f in files:
        ext = Path(f.filename).suffix
        fname = f"round_{round_id}_{uuid4().hex}{ext}"
        target = storage / fname
        target.write_bytes(f.file.read())
        meta = RoundPhoto(round_id=round_id, file_path=f"/storage/{fname}", uploaded_by=user.id)
        up = UploadMeta(original_name=f.filename, file_path=meta.file_path, uploaded_by=user.id)
        session.add(meta); session.add(up)
        saved.append(meta.file_path)
    session.commit()
    add_audit(session, user.id, "upload", "round_photos", round_id, f"{len(saved)} fotos")
    return {"files": saved}


@app.get("/rounds")
def list_rounds(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    q = select(Round)
    if user.role == Role.funcionario:
        q = q.where(Round.employee_id == user.id)
    if user.role == Role.morador:
        q = q.where(Round.unit_id == user.unit_id)
    return session.exec(q).all()


@app.post("/lock-windows")
def create_lock_window(data: LockWindowCreate, user: User = Depends(require_roles(Role.admin)), session: Session = Depends(get_session)):
    lock = LockWindow(**data.model_dump())
    session.add(lock); session.commit(); session.refresh(lock)
    add_audit(session, user.id, "create", "lock_window", lock.id)
    return lock


@app.get("/audit")
def list_audit(user: User = Depends(require_roles(Role.admin)), session: Session = Depends(get_session)):
    return session.exec(select(AuditEvent).order_by(AuditEvent.happened_at.desc())).all()


@app.get("/dashboard/finance")
def dashboard_finance(user: User = Depends(require_roles(Role.admin)), session: Session = Depends(get_session)):
    paid = session.exec(select(func.count(Payment.id)).where(Payment.status == PaymentStatus.pago)).one()
    pending = session.exec(select(func.count(Payment.id)).where(Payment.status == PaymentStatus.pendente)).one()
    late = session.exec(select(func.count(Payment.id)).where(Payment.status == PaymentStatus.atrasado)).one()
    return {"paid": paid, "pending": pending, "late": late, "inadimplencia_mensal": late}


@app.get("/dashboard/operations")
def dashboard_operations(user: User = Depends(require_roles(Role.admin)), session: Session = Depends(get_session)):
    rounds = session.exec(select(func.count(Round.id))).one()
    tickets_open = session.exec(select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.aberto)).one()
    coverages_pending = session.exec(select(func.count(Coverage.id)).where(Coverage.status == CoverageStatus.pendente)).one()
    return {"rounds_period": rounds, "tickets_open": tickets_open, "coverages_pending": coverages_pending}
