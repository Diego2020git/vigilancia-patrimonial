from datetime import datetime, timedelta, timezone
from typing import Optional
import hashlib
import base64
import bcrypt
from jose import jwt, JWTError
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from .config import settings
from .db import get_session
from .models import User, Role

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _prehash(password: str) -> bytes:
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest)


def hash_password(password: str) -> str:
    prehashed = _prehash(password)
    hashed = bcrypt.hashpw(prehashed, bcrypt.gensalt()).decode("utf-8")
    return f"sha256_bcrypt${hashed}"
pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hash_: str) -> bool:
    try:
        if hash_.startswith("sha256_bcrypt$"):
            stored = hash_.split("$", 1)[1].encode("utf-8")
            return bcrypt.checkpw(_prehash(password), stored)

        # backward compatibility with plain bcrypt hashes
        if hash_.startswith("$2"):
            return bcrypt.checkpw(password.encode("utf-8"), hash_.encode("utf-8"))

        return False
    except ValueError:
        return False
        return pwd_context.verify(password, hash_)
    except ValueError:
        return False
    return pwd_context.verify(password, hash_)


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
