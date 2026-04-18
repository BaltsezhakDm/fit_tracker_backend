from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.db.session import get_db
from src.infrastructure.repositories.user_repo import SQLAlchemyUserRepository
from src.infrastructure.repositories.exercise_repo import SQLAlchemyExerciseRepository
from src.infrastructure.repositories.program_repo import SQLAlchemyTrainingProgramRepository, SQLAlchemyTrainingPlanRepository, SQLAlchemyPlanExerciseRepository
from src.infrastructure.repositories.workout_repo import SQLAlchemyWorkoutSessionRepository, SQLAlchemyWorkoutExerciseRepository, SQLAlchemyWorkoutSetRepository
from src.infrastructure.repositories.analytics_repo import SQLAlchemyAnalyticsRepository
from src.application.services.user import UserService
from src.application.services.exercise import ExerciseService
from src.application.services.program import ProgramService
from src.application.services.workout import WorkoutService
from src.application.services.analytics import AnalyticsService

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    repo = SQLAlchemyUserRepository(db)
    return UserService(repo)

def get_exercise_service(db: AsyncSession = Depends(get_db)) -> ExerciseService:
    repo = SQLAlchemyExerciseRepository(db)
    return ExerciseService(repo)

def get_program_service(db: AsyncSession = Depends(get_db)) -> ProgramService:
    program_repo = SQLAlchemyTrainingProgramRepository(db)
    plan_repo = SQLAlchemyTrainingPlanRepository(db)
    plan_exercise_repo = SQLAlchemyPlanExerciseRepository(db)
    return ProgramService(program_repo, plan_repo, plan_exercise_repo)

def get_workout_service(db: AsyncSession = Depends(get_db)) -> WorkoutService:
    session_repo = SQLAlchemyWorkoutSessionRepository(db)
    exercise_repo = SQLAlchemyWorkoutExerciseRepository(db)
    set_repo = SQLAlchemyWorkoutSetRepository(db)
    return WorkoutService(session_repo, exercise_repo, set_repo)

def get_analytics_service(db: AsyncSession = Depends(get_db)) -> AnalyticsService:
    repo = SQLAlchemyAnalyticsRepository(db)
    return AnalyticsService(repo)
