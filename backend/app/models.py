from __future__ import annotations
from datetime import datetime, date, time
from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field


class Role(str, Enum):
    admin = "admin"
    funcionario = "funcionario"
    morador = "morador"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(index=True, unique=True)
    password_hash: str
    role: Role
    unit_id: Optional[int] = Field(default=None, foreign_key="unit.id")
    active: bool = True


class Unit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True)
    owner_name: str


class PaymentStatus(str, Enum):
    pago = "pago"
    pendente = "pendente"
    atrasado = "atrasado"


class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    unit_id: int = Field(foreign_key="unit.id", index=True)
    due_date: date
    amount: float
    status: PaymentStatus = PaymentStatus.pendente


class AgendaType(str, Enum):
    mudanca = "mudanca"
    prestador = "prestador"
    visita = "visita"
    saida = "saida"


class AgendaStatus(str, Enum):
    pendente = "pendente"
    aprovado = "aprovado"
    recusado = "recusado"


class Agenda(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    unit_id: int = Field(foreign_key="unit.id", index=True)
    requester_id: int = Field(foreign_key="user.id")
    type: AgendaType
    start_at: datetime = Field(index=True)
    end_at: datetime
    description: str
    status: AgendaStatus = AgendaStatus.pendente
    requires_approval: bool = False


class LockWindow(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    start_time: time
    end_time: time
    enabled: bool = True


class CoverageStatus(str, Enum):
    pendente = "pendente"
    em_andamento = "em_andamento"
    concluida = "concluida"


class Coverage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    unit_id: int = Field(foreign_key="unit.id", index=True)
    from_agenda_id: int = Field(foreign_key="agenda.id")
    title: str
    assigned_to: Optional[int] = Field(default=None, foreign_key="user.id")
    status: CoverageStatus = CoverageStatus.pendente


class TicketStatus(str, Enum):
    aberto = "aberto"
    em_atendimento = "em_atendimento"
    resolvido = "resolvido"


class Ticket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    unit_id: int = Field(foreign_key="unit.id")
    opened_by: int = Field(foreign_key="user.id")
    assigned_to: Optional[int] = Field(default=None, foreign_key="user.id")
    title: str
    description: str
    status: TicketStatus = TicketStatus.aberto


class Round(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    unit_id: int = Field(foreign_key="unit.id")
    employee_id: int = Field(foreign_key="user.id")
    location: str
    happened_at: datetime = Field(default_factory=datetime.utcnow)
    observation: str = ""


class RoundPhoto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    round_id: int = Field(foreign_key="round.id")
    file_path: str
    uploaded_by: int = Field(foreign_key="user.id")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class UploadMeta(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    original_name: str
    file_path: str
    uploaded_by: int = Field(foreign_key="user.id")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class AuditEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    action: str
    entity: str
    entity_id: Optional[int] = None
    happened_at: datetime = Field(default_factory=datetime.utcnow)
    details: str = ""


class PublicConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    brand_name: str = "Vigilância Patrimonial"
    primary_color: str = "#14b8a6"
    secondary_color: str = "#1f2937"
    logo_path: str = "/logo.svg"
