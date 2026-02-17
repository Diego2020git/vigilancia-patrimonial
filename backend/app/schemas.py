from datetime import datetime, date, time
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from .models import Role, AgendaType, AgendaStatus, PaymentStatus, TicketStatus, CoverageStatus


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    role: Role
    unit_id: Optional[int] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Role
    unit_id: Optional[int] = None


class UnitCreate(BaseModel):
    code: str
    owner_name: str


class PaymentCreate(BaseModel):
    unit_id: int
    due_date: date
    amount: float
    status: PaymentStatus = PaymentStatus.pendente


class AgendaCreate(BaseModel):
    unit_id: int
    type: AgendaType
    start_at: datetime
    end_at: datetime
    description: str


class AgendaApprove(BaseModel):
    status: AgendaStatus


class CoverageAssign(BaseModel):
    assigned_to: int
    status: CoverageStatus = CoverageStatus.em_andamento


class TicketCreate(BaseModel):
    unit_id: int
    title: str
    description: str


class TicketUpdate(BaseModel):
    status: TicketStatus
    assigned_to: Optional[int] = None


class RoundCreate(BaseModel):
    unit_id: int
    location: str
    happened_at: datetime
    observation: str = ""


class LockWindowCreate(BaseModel):
    start_time: time
    end_time: time
    enabled: bool = True


class PublicConfigUpdate(BaseModel):
    brand_name: str
    primary_color: str
    secondary_color: str
