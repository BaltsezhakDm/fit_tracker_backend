from fastapi import APIRouter, Depends, HTTPException
from src.api.schemas.schemas import UserCreate, UserRead
from src.application.services.user import UserService
from src.api.dependencies import get_user_service, get_current_user
from src.domain.entities import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user.
    """
    return current_user

@router.post("/", response_model=UserRead)
async def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    """
    Register a new user.
    """
    existing = await service.get_user_by_telegram_id(user.telegram_id)
    if existing:
        return existing
    return await service.create_user(**user.model_dump())

@router.get("/telegram/{telegram_id}", response_model=UserRead)
async def get_user(telegram_id: int, service: UserService = Depends(get_user_service)):
    """
    Get user by Telegram ID.
    """
    user = await service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
