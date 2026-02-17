from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from .config import settings
from .db import get_session
from .models import User, Role

pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hash_: str) -> bool:
    try:
        return pwd_context.verify(password, hash_)
    except ValueError:
        return False


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        sub = payload.get("sub")
        if not sub:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = session.exec(select(User).where(User.email == sub)).first()
    if not user or not user.active:
        raise credentials_exception
    return user


def require_roles(*roles: Role):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Sem permissão para este recurso")
        return user
    return checker
