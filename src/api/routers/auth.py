import hashlib
import hmac
import json
import time
import urllib.parse
from datetime import datetime, timedelta, UTC
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
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

def verify_telegram_data(init_data: str) -> Dict[str, Any]:
    """
    Verifies the authenticity of data received from the Telegram Mini App.

    Args:
        init_data: The raw initData string from Telegram.

    Returns:
        The user data dictionary if verification is successful.

    Raises:
        HTTPException: If verification fails or data is invalid.
    """
    try:
        # Use parse_qsl to correctly handle URL-encoded data
        params = dict(urllib.parse.parse_qsl(init_data, strict_parsing=True))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid initData format"
        )

    if "hash" not in params:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing hash in initData"
        )

    telegram_hash = params.pop("hash")
    # The data_check_string is built from sorted key-value pairs, excluding the hash
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(params.items())
    )

    secret_key = hmac.new(
        b"WebAppData",
        settings.TELEGRAM_BOT_TOKEN.encode(),
        hashlib.sha256
    ).digest()
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    if calculated_hash != telegram_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram signature"
        )

    # Check auth_date for freshness (24 hours)
    if "auth_date" in params:
        try:
            auth_date = int(params["auth_date"])
            if time.time() - auth_date > 86400:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Auth data expired"
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid auth_date"
            )

    user_json = params.get("user")
    if not user_json:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing user data"
        )

    try:
        user_data = json.loads(user_json)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user JSON"
        )

    return user_data

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token.

    Args:
        data: The payload to encode.
        expires_delta: Optional expiration time delta.

    Returns:
        The encoded JWT token.
    """
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
) -> Dict[str, str]:
    """
    Authenticates a user via Telegram Mini App initData.

    Args:
        auth_data: The Telegram authentication request containing initData.
        user_service: The user service instance.

    Returns:
        A dictionary containing access and refresh tokens.
    """
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
