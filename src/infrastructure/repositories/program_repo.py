from typing import List, Optional
from sqlalchemy import select
from src.domain.entities import TrainingProgram, TrainingPlan, PlanExercise
from src.domain.repositories import TrainingProgramRepository, TrainingPlanRepository
from src.infrastructure.db.models import TrainingProgramModel, TrainingPlanModel, PlanExerciseModel
from src.infrastructure.repositories.base_repo import SQLAlchemyBaseRepository

class SQLAlchemyTrainingProgramRepository(SQLAlchemyBaseRepository[TrainingProgram, TrainingProgramModel], TrainingProgramRepository):
    def __init__(self, session):
        super().__init__(session, TrainingProgramModel)

    async def get_by_user_id(self, user_id: int) -> List[TrainingProgram]:
        stmt = select(TrainingProgramModel).where(TrainingProgramModel.user_id == user_id)
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, m: TrainingProgramModel) -> TrainingProgram:
        return TrainingProgram(id=m.id, user_id=m.user_id, name=m.name, description=m.description)

    def _to_model(self, e: TrainingProgram) -> TrainingProgramModel:
        return TrainingProgramModel(id=e.id, user_id=e.user_id, name=e.name, description=e.description)

class SQLAlchemyTrainingPlanRepository(SQLAlchemyBaseRepository[TrainingPlan, TrainingPlanModel], TrainingPlanRepository):
    def __init__(self, session):
        super().__init__(session, TrainingPlanModel)

    async def get_by_program_id(self, program_id: int) -> List[TrainingPlan]:
        stmt = select(TrainingPlanModel).where(TrainingPlanModel.program_id == program_id)
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, m: TrainingPlanModel) -> TrainingPlan:
        return TrainingPlan(id=m.id, program_id=m.program_id, name=m.name, day_of_week=m.day_of_week)

    def _to_model(self, e: TrainingPlan) -> TrainingPlanModel:
        return TrainingPlanModel(id=e.id, program_id=e.program_id, name=e.name, day_of_week=e.day_of_week)

from src.domain.repositories import TrainingProgramRepository, TrainingPlanRepository, PlanExerciseRepository

class SQLAlchemyPlanExerciseRepository(PlanExerciseRepository):
    def __init__(self, session):
        self.session = session

    async def add_exercise_to_plan(self, plan_exercise: PlanExercise) -> None:
        m = PlanExerciseModel(
            plan_id=plan_exercise.plan_id,
            exercise_id=plan_exercise.exercise_id,
            target_sets=plan_exercise.target_sets,
            target_reps=plan_exercise.target_reps
        )
        self.session.add(m)
        await self.session.commit()

    async def get_exercises_by_plan_id(self, plan_id: int) -> List[PlanExercise]:
        stmt = select(PlanExerciseModel).where(PlanExerciseModel.plan_id == plan_id)
        result = await self.session.execute(stmt)
        return [PlanExercise(plan_id=m.plan_id, exercise_id=m.exercise_id, target_sets=m.target_sets, target_reps=m.target_reps) for m in result.scalars().all()]

    async def remove_exercise_from_plan(self, plan_id: int, exercise_id: int) -> None:
        from sqlalchemy import delete
        stmt = delete(PlanExerciseModel).where(
            PlanExerciseModel.plan_id == plan_id,
            PlanExerciseModel.exercise_id == exercise_id
        )
        await self.session.execute(stmt)
        await self.session.commit()
