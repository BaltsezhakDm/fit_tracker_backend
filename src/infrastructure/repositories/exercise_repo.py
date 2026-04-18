from typing import List
from sqlalchemy import select, and_, not_
from src.domain.entities import Exercise
from src.domain.repositories import ExerciseRepository
from src.infrastructure.db.models import ExerciseModel, UserBlacklistedExerciseModel
from src.infrastructure.repositories.base_repo import SQLAlchemyBaseRepository

class SQLAlchemyExerciseRepository(SQLAlchemyBaseRepository[Exercise, ExerciseModel], ExerciseRepository):
    def __init__(self, session):
        super().__init__(session, ExerciseModel)

    def _to_entity(self, m: ExerciseModel) -> Exercise:
        return Exercise(
            id=m.id,
            name=m.name,
            primary_muscle_group=m.primary_muscle_group,
            secondary_muscle_groups=m.secondary_muscle_groups,
            description=m.description,
            media_url=m.media_url,
            comment=m.comment,
            biomechanics_tags=m.biomechanics_tags
        )

    def _to_model(self, e: Exercise) -> ExerciseModel:
        return ExerciseModel(
            id=e.id,
            name=e.name,
            primary_muscle_group=e.primary_muscle_group,
            secondary_muscle_groups=e.secondary_muscle_groups,
            description=e.description,
            media_url=e.media_url,
            comment=e.comment,
            biomechanics_tags=e.biomechanics_tags
        )

    async def get_all_for_user(self, user_id: int) -> List[Exercise]:
        blacklist_stmt = select(UserBlacklistedExerciseModel.exercise_id).where(UserBlacklistedExerciseModel.user_id == user_id)
        stmt = select(ExerciseModel).where(not_(ExerciseModel.id.in_(blacklist_stmt)))
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def blacklist_exercise(self, user_id: int, exercise_id: int) -> None:
        blacklisted = UserBlacklistedExerciseModel(user_id=user_id, exercise_id=exercise_id)
        self.session.add(blacklisted)
        await self.session.commit()
