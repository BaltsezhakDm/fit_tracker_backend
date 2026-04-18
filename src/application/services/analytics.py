from typing import List, Dict, Any
from src.domain.repositories import AnalyticsRepository
from src.domain.value_objects import ExerciseProgression

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
