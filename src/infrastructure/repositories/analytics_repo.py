from typing import List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.repositories import AnalyticsRepository
from src.domain.value_objects import ExerciseProgression
from src.infrastructure.db.models import WorkoutSessionModel, WorkoutExerciseModel, WorkoutSetModel

class SQLAlchemyAnalyticsRepository(AnalyticsRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_exercise_progression(self, user_id: int, exercise_id: int) -> List[ExerciseProgression]:
        stmt = (
            select(
                WorkoutSessionModel.start_time,
                func.max(WorkoutSetModel.weight).label("max_weight"),
                func.sum(WorkoutSetModel.weight * WorkoutSetModel.reps).label("total_volume")
            )
            .join(WorkoutExerciseModel, WorkoutSessionModel.id == WorkoutExerciseModel.session_id)
            .join(WorkoutSetModel, WorkoutExerciseModel.id == WorkoutSetModel.workout_exercise_id)
            .where(WorkoutSessionModel.user_id == user_id)
            .where(WorkoutExerciseModel.exercise_id == exercise_id)
            .group_by(WorkoutSessionModel.id)
            .order_by(WorkoutSessionModel.start_time)
        )

        result = await self.session.execute(stmt)
        return [
            ExerciseProgression(
                date=row.start_time,
                max_weight=row.max_weight,
                total_volume=row.total_volume
            )
            for row in result.all()
        ]
