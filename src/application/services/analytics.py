from typing import List, Dict, Any
from src.domain.repositories import AnalyticsRepository
from src.domain.value_objects import ExerciseProgression, AnalyticsSummary, WorkloadData, PersonalRecord

class AnalyticsService:
    """
    Сервис для расчета статистики и аналитики прогресса.
    """
    def __init__(self, analytics_repo: AnalyticsRepository):
        self.analytics_repo = analytics_repo

    async def get_exercise_progression(self, user_id: int, exercise_id: int) -> List[ExerciseProgression]:
        """
        Возвращает прогрессию весов по конкретному упражнению.
        """
        return await self.analytics_repo.get_exercise_progression(user_id, exercise_id)

    async def get_summary(self, user_id: int) -> AnalyticsSummary:
        """
        Получение сводной статистики пользователя.
        """
        return await self.analytics_repo.get_summary(user_id)

    async def get_workload(self, user_id: int, period: str) -> List[WorkloadData]:
        """
        Данные для графика нагрузки по дням.
        """
        return await self.analytics_repo.get_workload(user_id, period)

    async def get_records(self, user_id: int) -> List[PersonalRecord]:
        """
        Список личных рекордов пользователя по упражнениям.
        """
        return await self.analytics_repo.get_records(user_id)
