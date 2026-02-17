from datetime import datetime, time
from sqlmodel import Session, select
from .models import Agenda, LockWindow, AuditEvent


def in_lock_window(start: datetime, end: datetime, lock: LockWindow) -> bool:
    if not lock.enabled:
        return False
    s, e = lock.start_time, lock.end_time
    def inside(t: time) -> bool:
        if s <= e:
            return s <= t <= e
        return t >= s or t <= e
    return inside(start.time()) or inside(end.time())


def has_overlap(session: Session, unit_id: int, start: datetime, end: datetime) -> bool:
    rows = session.exec(select(Agenda).where(Agenda.unit_id == unit_id)).all()
    for row in rows:
        if start < row.end_at and end > row.start_at:
            return True
    return False


def add_audit(session: Session, user_id: int | None, action: str, entity: str, entity_id: int | None = None, details: str = ""):
    event = AuditEvent(user_id=user_id, action=action, entity=entity, entity_id=entity_id, details=details)
    session.add(event)
    session.commit()
