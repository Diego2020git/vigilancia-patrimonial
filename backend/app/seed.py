from datetime import date, datetime, timedelta, time
from sqlmodel import Session, select
from .models import User, Unit, Payment, LockWindow, PublicConfig, Role, Ticket, Agenda, AgendaType, AgendaStatus
from .auth import hash_password


def seed_data(session: Session):
    if session.exec(select(User)).first():
        return

    u1 = Unit(code="A101", owner_name="Carlos Silva")
    u2 = Unit(code="B202", owner_name="Ana Souza")
    session.add(u1)
    session.add(u2)
    session.commit()
    session.refresh(u1)

    admin = User(name="Admin", email="admin@vp.local", password_hash=hash_password("admin123"), role=Role.admin)
    func = User(name="João Vigilante", email="func@vp.local", password_hash=hash_password("func123"), role=Role.funcionario)
    mor = User(name="Carlos Morador", email="morador@vp.local", password_hash=hash_password("morador123"), role=Role.morador, unit_id=u1.id)
    session.add(admin)
    session.add(func)
    session.add(mor)

    session.add(LockWindow(start_time=time(22, 0), end_time=time(6, 0), enabled=True))
    session.add(PublicConfig())

    session.add(Payment(unit_id=u1.id, due_date=date.today(), amount=550.0, status="pendente"))
    session.add(Payment(unit_id=u2.id, due_date=date.today() - timedelta(days=30), amount=550.0, status="atrasado"))

    session.add(Ticket(unit_id=u1.id, opened_by=1, assigned_to=2, title="Portão", description="Portão com ruído", status="aberto"))

    now = datetime.now()
    session.add(Agenda(unit_id=u1.id, requester_id=1, type=AgendaType.visita, start_at=now + timedelta(days=1), end_at=now + timedelta(days=1, hours=1), description="Visita familiar", status=AgendaStatus.pendente, requires_approval=True))

    session.commit()
