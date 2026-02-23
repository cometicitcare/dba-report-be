"""
Buddhist Affairs MIS Dashboard - Authentication Router
Handles login and JWT token issuance/validation.
Credentials are read from the .env file — no database required.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ── OAuth2 scheme — tells FastAPI where to look for the token ──
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


# ── Pydantic schemas ──────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserInfo(BaseModel):
    username: str


# ── Helpers ──────────────────────────────────────────────────

def _create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Encode a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _verify_token(token: str) -> str:
    """Decode and validate a JWT token; returns the username."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


# ── Dependency — inject into protected routes ─────────────────

async def require_auth(token: str = Depends(oauth2_scheme)) -> str:
    """
    FastAPI dependency.  Raises 401 if the token is missing or invalid.
    Usage:
        @router.get("/something")
        async def endpoint(user: str = Depends(require_auth)):
            ...
    """
    return _verify_token(token)


# ── Routes ────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse, summary="Login and receive JWT token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate with username / password (from .env).
    Returns a Bearer JWT token to use on all subsequent API requests.
    """
    # Compare credentials stored in .env (constant-time comparison via hmac is overkill
    # for an internal tool, but we do simple equality here — credentials live only in env)
    valid_user = form_data.username == settings.AUTH_USERNAME
    valid_pass = form_data.password == settings.AUTH_PASSWORD

    if not (valid_user and valid_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expire_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = _create_access_token({"sub": form_data.username}, expires_delta=expire_delta)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=int(expire_delta.total_seconds()),
    )


@router.get("/me", response_model=UserInfo, summary="Return currently authenticated user")
async def get_me(username: str = Depends(require_auth)):
    """Returns the username of the currently authenticated user."""
    return UserInfo(username=username)
