from src.domain.entities import Exercise
from src.domain.repositories import ExerciseRepository
from src.infrastructure.db.models import ExerciseModel
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
            comment=m.comment
        )

    def _to_model(self, e: Exercise) -> ExerciseModel:
        return ExerciseModel(
            id=e.id,
            name=e.name,
            primary_muscle_group=e.primary_muscle_group,
            secondary_muscle_groups=e.secondary_muscle_groups,
            description=e.description,
            media_url=e.media_url,
            comment=e.comment
        )
