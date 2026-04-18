from typing import List
from fastapi import APIRouter, Depends
from src.api.schemas.schemas import ProgressionRead
from src.application.services.analytics import AnalyticsService
from src.api.dependencies import get_analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/user/{user_id}/exercise/{exercise_id}/progression", response_model=List[ProgressionRead])
async def get_progression(user_id: int, exercise_id: int, service: AnalyticsService = Depends(get_analytics_service)):
    return await service.get_exercise_progression(user_id, exercise_id)
