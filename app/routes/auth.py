"""
routes/auth.py
--------------
Authentication & Route Protection dependencies for FastAPI.
Endpoints:
- POST /auth/signup
- POST /auth/login
- GET /auth/me
"""

import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Header, status
from pydantic import BaseModel, EmailStr, Field

from app.services.database_manager import DatabaseManager
from app.services.auth_service import hash_password, verify_password, create_access_token, decode_token

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
router = auth_router
db = DatabaseManager()



# ---------- SCHEMAS ----------
class UserSignup(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field(..., pattern="^(citizen|admin)$")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    token: str
    user_id: str
    name: str
    email: str
    role: str


# ---------- DEPENDENCIES ----------
def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Bearer token missing."
        )
    token = authorization.split(" ")[1]
    try:
        payload = decode_token(token)
        return payload
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required."
        )
    return user


# ---------- ENDPOINTS ----------
@auth_router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: UserSignup):
    existing = db.get_user_by_email(payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    user_id = f"USR-{uuid.uuid4().hex[:8].upper()}"
    pwd_hash = hash_password(payload.password)

    user_data = {
        "user_id": user_id,
        "name": payload.name,
        "email": payload.email.lower().strip(),
        "password_hash": pwd_hash,
        "role": payload.role
    }

    success = db.create_user(user_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user."
        )

    token = create_access_token(user_id=user_id, role=payload.role, name=payload.name, email=payload.email)

    return {
        "token": token,
        "user_id": user_id,
        "name": payload.name,
        "email": payload.email,
        "role": payload.role
    }


@auth_router.post("/login", response_model=AuthResponse)
def login(payload: UserLogin):
    user = db.get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    token = create_access_token(
        user_id=user["user_id"],
        role=user["role"],
        name=user["name"],
        email=user["email"]
    )

    return {
        "token": token,
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"]
    }


@auth_router.get("/me")
def get_me(user: dict = Depends(get_current_user)):
    user_record = db.get_user_by_id(user["user_id"])
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_id": user_record["user_id"],
        "name": user_record["name"],
        "email": user_record["email"],
        "role": user_record["role"],
        "created_at": user_record["created_at"]
    }
