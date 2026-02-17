from datetime import date, datetime, timedelta, time
from sqlmodel import Session, select
from .models import User, Unit, Payment, LockWindow, PublicConfig, Role, Ticket, Agenda, AgendaType, AgendaStatus
from .auth import hash_password


def _get_or_create_unit(session: Session, code: str, owner_name: str) -> Unit:
    unit = session.exec(select(Unit).where(Unit.code == code)).first()
    if unit:
        return unit
    unit = Unit(code=code, owner_name=owner_name)
    session.add(unit)
    session.commit()
    session.refresh(unit)
    return unit


def _upsert_demo_user(
    session: Session,
    *,
    name: str,
    email: str,
    plain_password: str,
    role: Role,
    unit_id: int | None = None,
) -> User:
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        user = User(name=name, email=email, password_hash=hash_password(plain_password), role=role, unit_id=unit_id)
    else:
        user.name = name
        user.role = role
        user.unit_id = unit_id
        user.password_hash = hash_password(plain_password)
        user.active = True
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def seed_data(session: Session):
    u1 = _get_or_create_unit(session, code="A101", owner_name="Carlos Silva")
    u2 = _get_or_create_unit(session, code="B202", owner_name="Ana Souza")

    admin = _upsert_demo_user(
        session,
        name="Admin",
        email="admin@vp.local",
        plain_password="admin123",
        role=Role.admin,
    )
    func = _upsert_demo_user(
        session,
        name="João Vigilante",
        email="func@vp.local",
        plain_password="func123",
        role=Role.funcionario,
    )
    mor = _upsert_demo_user(
        session,
        name="Carlos Morador",
        email="morador@vp.local",
        plain_password="morador123",
        role=Role.morador,
        unit_id=u1.id,
    )

    if not session.exec(select(LockWindow)).first():
        session.add(LockWindow(start_time=time(22, 0), end_time=time(6, 0), enabled=True))

    if not session.exec(select(PublicConfig)).first():
        session.add(PublicConfig())

    if not session.exec(select(Payment)).first():
        session.add(Payment(unit_id=u1.id, due_date=date.today(), amount=550.0, status="pendente"))
        session.add(Payment(unit_id=u2.id, due_date=date.today() - timedelta(days=30), amount=550.0, status="atrasado"))

    if not session.exec(select(Ticket)).first():
        session.add(
            Ticket(
                unit_id=u1.id,
                opened_by=admin.id,
                assigned_to=func.id,
                title="Portão",
                description="Portão com ruído",
                status="aberto",
            )
        )

    if not session.exec(select(Agenda)).first():
        now = datetime.now()
        session.add(
            Agenda(
                unit_id=u1.id,
                requester_id=mor.id,
                type=AgendaType.visita,
                start_at=now + timedelta(days=1),
                end_at=now + timedelta(days=1, hours=1),
                description="Visita familiar",
                status=AgendaStatus.pendente,
                requires_approval=True,
            )
        )

    session.commit()
