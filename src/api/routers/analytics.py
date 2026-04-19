from typing import List
from fastapi import APIRouter, Depends, Query
from src.api.schemas.schemas import ProgressionRead, AnalyticsSummaryRead, WorkloadDataRead, PersonalRecordRead
from src.application.services.analytics import AnalyticsService
from src.api.dependencies import get_analytics_service, get_current_user
from src.domain.entities import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary", response_model=AnalyticsSummaryRead)
async def get_summary(
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Получение сводной статистики пользователя.
    """
    return await service.get_summary(current_user.id)

@router.get("/workload", response_model=List[WorkloadDataRead])
async def get_workload(
    period: str = Query("week", enum=["week", "month"]),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Данные для графика нагрузки по дням.
    """
    return await service.get_workload(current_user.id, period)

@router.get("/records", response_model=List[PersonalRecordRead])
async def get_records(
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Список личных рекордов пользователя по упражнениям.
    """
    return await service.get_records(current_user.id)

@router.get("/user/{user_id}/exercise/{exercise_id}/progression", response_model=List[ProgressionRead])
async def get_progression(user_id: int, exercise_id: int, service: AnalyticsService = Depends(get_analytics_service)):
    return await service.get_exercise_progression(user_id, exercise_id)
