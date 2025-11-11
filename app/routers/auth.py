from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.repo import dao
from app.utils import ids
from app.utils.config import get_settings

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: str = Field(min_length=2, max_length=64)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class AuthResponse(BaseModel):
    trace_id: str
    access_token: str
    token_type: str = "bearer"
    expires_in: int


def _hash_password(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _encode_segment(payload: dict[str, str | int]) -> str:
    return base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode()
    ).rstrip(b"=").decode("utf-8")


def _sign_jwt(payload: dict[str, str | int]) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_segment = _encode_segment(header)
    payload_segment = _encode_segment(payload)
    signing_input = f"{header_segment}.{payload_segment}".encode()
    signature = hmac.new(settings.jwt_secret.encode(), signing_input, hashlib.sha256).digest()
    signature_segment = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("utf-8")
    return f"{header_segment}.{payload_segment}.{signature_segment}"


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest) -> AuthResponse:
    trace_id = ids.new_trace_id()
    existing = dao.get_user_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    password_hash = _hash_password(payload.password)
    user = dao.create_user(
        email=payload.email,
        password_hash=password_hash,
        display_name=payload.display_name,
    )
    exp = int(time.time()) + 3600
    token = _sign_jwt({"sub": user["id"], "email": user["email"], "exp": exp})
    return AuthResponse(trace_id=trace_id, access_token=token, expires_in=3600)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest) -> AuthResponse:
    trace_id = ids.new_trace_id()
    user = dao.get_user_by_email(payload.email)
    if not user or user["password_hash"] != _hash_password(payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    exp = int(time.time()) + 3600
    token = _sign_jwt({"sub": user["id"], "email": user["email"], "exp": exp})
    return AuthResponse(trace_id=trace_id, access_token=token, expires_in=3600)
