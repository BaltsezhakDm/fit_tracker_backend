import hashlib
import hmac
import time
from datetime import datetime, timedelta, UTC
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel
from src.core.config import settings
from src.application.services.user import UserService
from src.api.dependencies import get_user_service

router = APIRouter(prefix="/auth", tags=["Auth"])

class TelegramAuthRequest(BaseModel):
    initData: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

def verify_telegram_data(init_data: str) -> dict:
    """
    Verifies the authenticity of data received from the Telegram Mini App.
    """
    try:
        vals = {k: v for k, v in [item.split("=") for item in init_data.split("&")]}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid initData format")

    if "hash" not in vals:
        raise HTTPException(status_code=400, detail="Missing hash in initData")

    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(vals.items()) if k != "hash"])
    secret_key = hmac.new(b"WebAppData", settings.TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if calculated_hash != vals["hash"]:
        raise HTTPException(status_code=401, detail="Invalid Telegram signature")

    # Optional: check auth_date for freshness
    if "auth_date" in vals:
        auth_date = int(vals["auth_date"])
        if time.time() - auth_date > 86400: # 24 hours
             raise HTTPException(status_code=401, detail="Auth data expired")

    import json
    user_data = json.loads(vals.get("user", "{}"))
    return user_data

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.post("/telegram", response_model=TokenResponse)
async def auth_telegram(
    auth_data: TelegramAuthRequest,
    user_service: UserService = Depends(get_user_service)
):
    # In a real scenario with a real bot token, we'd verify it.
    # For now, we'll allow a "mock" mode if the token is "your_bot_token"
    if settings.TELEGRAM_BOT_TOKEN == "your_bot_token":
        # Mock user data for development
        user_info = {"id": 123456, "username": "test_user"}
    else:
        user_info = verify_telegram_data(auth_data.initData)

    telegram_id = user_info.get("id")
    if not telegram_id:
        raise HTTPException(status_code=400, detail="Invalid user data from Telegram")

    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        user = await user_service.create_user(telegram_id=telegram_id, username=user_info.get("username"))

    access_token = create_access_token(data={"sub": str(user.id), "tg_id": telegram_id})
    # For simplicity in MVP, refresh_token is the same or a longer-lived one
    refresh_token = create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(days=30))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
