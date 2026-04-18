from typing import List, Optional
from sqlalchemy import select
from src.domain.entities import WorkoutSession, WorkoutExercise, WorkoutSet, WorkoutStatus
from src.domain.repositories import WorkoutSessionRepository, WorkoutExerciseRepository, WorkoutSetRepository
from src.infrastructure.db.models import WorkoutSessionModel, WorkoutExerciseModel, WorkoutSetModel
from src.infrastructure.repositories.base_repo import SQLAlchemyBaseRepository

class SQLAlchemyWorkoutSessionRepository(SQLAlchemyBaseRepository[WorkoutSession, WorkoutSessionModel], WorkoutSessionRepository):
    def __init__(self, session):
        super().__init__(session, WorkoutSessionModel)

    async def get_active_session_by_user_id(self, user_id: int) -> Optional[WorkoutSession]:
        stmt = select(WorkoutSessionModel).where(
            WorkoutSessionModel.user_id == user_id,
            WorkoutSessionModel.status == WorkoutStatus.ACTIVE
        )
        result = await self.session.execute(stmt)
        m = result.scalar_one_or_none()
        return self._to_entity(m) if m else None

    async def get_history_by_user_id(self, user_id: int) -> List[WorkoutSession]:
        stmt = select(WorkoutSessionModel).where(WorkoutSessionModel.user_id == user_id)
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, m: WorkoutSessionModel) -> WorkoutSession:
        return WorkoutSession(
            id=m.id, user_id=m.user_id, plan_id=m.plan_id,
            start_time=m.start_time, end_time=m.end_time, status=m.status
        )

    def _to_model(self, e: WorkoutSession) -> WorkoutSessionModel:
        return WorkoutSessionModel(
            id=e.id, user_id=e.user_id, plan_id=e.plan_id,
            start_time=e.start_time, end_time=e.end_time, status=e.status
        )

class SQLAlchemyWorkoutExerciseRepository(SQLAlchemyBaseRepository[WorkoutExercise, WorkoutExerciseModel], WorkoutExerciseRepository):
    def __init__(self, session):
        super().__init__(session, WorkoutExerciseModel)

    async def get_by_session_id(self, session_id: int) -> List[WorkoutExercise]:
        stmt = select(WorkoutExerciseModel).where(WorkoutExerciseModel.session_id == session_id).order_by(WorkoutExerciseModel.order)
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, m: WorkoutExerciseModel) -> WorkoutExercise:
        return WorkoutExercise(id=m.id, session_id=m.session_id, exercise_id=m.exercise_id, order=m.order)

    def _to_model(self, e: WorkoutExercise) -> WorkoutExerciseModel:
        return WorkoutExerciseModel(id=e.id, session_id=e.session_id, exercise_id=e.exercise_id, order=e.order)

class SQLAlchemyWorkoutSetRepository(SQLAlchemyBaseRepository[WorkoutSet, WorkoutSetModel], WorkoutSetRepository):
    def __init__(self, session):
        super().__init__(session, WorkoutSetModel)

    async def get_by_workout_exercise_id(self, workout_exercise_id: int) -> List[WorkoutSet]:
        stmt = select(WorkoutSetModel).where(WorkoutSetModel.workout_exercise_id == workout_exercise_id)
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, m: WorkoutSetModel) -> WorkoutSet:
        return WorkoutSet(
            id=m.id, workout_exercise_id=m.workout_exercise_id,
            reps=m.reps, weight=m.weight,
            time_spent_seconds=m.time_spent_seconds, rest_time_seconds=m.rest_time_seconds
        )

    def _to_model(self, e: WorkoutSet) -> WorkoutSetModel:
        return WorkoutSetModel(
            id=e.id, workout_exercise_id=e.workout_exercise_id,
            reps=e.reps, weight=e.weight,
            time_spent_seconds=e.time_spent_seconds, rest_time_seconds=e.rest_time_seconds
        )
