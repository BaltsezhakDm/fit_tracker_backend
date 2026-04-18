from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import settings
from src.domain.entities import User
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/telegram")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await user_service.get_user(int(user_id))
    if user is None:
        raise credentials_exception
    return user
