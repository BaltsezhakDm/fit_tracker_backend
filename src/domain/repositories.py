from abc import ABC, abstractmethod
from typing import List, Optional, Generic, TypeVar, Any
from src.domain.entities import (
    User, Exercise, TrainingProgram, TrainingPlan,
    WorkoutSession, WorkoutExercise, WorkoutSet, PlanExercise
)

T = TypeVar("T")

class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository with common CRUD operations.
    """
    @abstractmethod
    async def get_by_id(self, id: Any) -> Optional[T]:
        """Get entity by its ID."""
        pass

    @abstractmethod
    async def get_all(self) -> List[T]:
        """Get all entities of this type."""
        pass

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity."""
        pass

    @abstractmethod
    async def update(self, entity: T) -> Optional[T]:
        """Update an existing entity."""
        pass

    @abstractmethod
    async def delete(self, id: Any) -> None:
        """Delete an entity by its ID."""
        pass

class UserRepository(BaseRepository[User], ABC):
    """Repository interface for User entities."""
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by their unique Telegram ID."""
        pass

class ExerciseRepository(BaseRepository[Exercise], ABC):
    """Repository interface for Exercise entities."""
    @abstractmethod
    async def get_all_for_user(self, user_id: int) -> List[Exercise]:
        """Get all exercises excluding blacklisted for user."""
        pass

    @abstractmethod
    async def blacklist_exercise(self, user_id: int, exercise_id: int) -> None:
        """Add exercise to user's blacklist."""
        pass

class TrainingProgramRepository(BaseRepository[TrainingProgram], ABC):
    """Repository interface for TrainingProgram entities."""
    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> List[TrainingProgram]:
        """Get all programs for a specific user."""
        pass

class TrainingPlanRepository(BaseRepository[TrainingPlan], ABC):
    """Repository interface for TrainingPlan entities."""
    @abstractmethod
    async def get_by_program_id(self, program_id: int) -> List[TrainingPlan]:
        """Get all plans for a specific program."""
        pass

class WorkoutSessionRepository(BaseRepository[WorkoutSession], ABC):
    """Repository interface for WorkoutSession entities."""
    @abstractmethod
    async def get_active_session_by_user_id(self, user_id: int) -> Optional[WorkoutSession]:
        """Get currently active session for a user."""
        pass

    @abstractmethod
    async def get_history_by_user_id(self, user_id: int) -> List[WorkoutSession]:
        """Get workout history for a user."""
        pass

class WorkoutExerciseRepository(BaseRepository[WorkoutExercise], ABC):
    """Repository interface for WorkoutExercise entities."""
    @abstractmethod
    async def get_by_session_id(self, session_id: int) -> List[WorkoutExercise]:
        """Get all exercises performed in a session."""
        pass

class WorkoutSetRepository(BaseRepository[WorkoutSet], ABC):
    """Repository interface for WorkoutSet entities."""
    @abstractmethod
    async def get_by_workout_exercise_id(self, workout_exercise_id: int) -> List[WorkoutSet]:
        """Get all sets for a specific workout exercise."""
        pass

class PlanExerciseRepository(ABC):
    """Repository interface for PlanExercise associations."""
    @abstractmethod
    async def add_exercise_to_plan(self, plan_exercise: PlanExercise) -> None:
        """Add an exercise to a plan."""
        pass

    @abstractmethod
    async def get_exercises_by_plan_id(self, plan_id: int) -> List[PlanExercise]:
        """Get all exercises for a plan."""
        pass

    @abstractmethod
    async def remove_exercise_from_plan(self, plan_id: int, exercise_id: int) -> None:
        """Remove an exercise from a plan."""
        pass

from src.domain.value_objects import ExerciseProgression

class AnalyticsRepository(ABC):
    """Repository interface for analytical data."""
    @abstractmethod
    async def get_exercise_progression(self, user_id: int, exercise_id: int) -> List[ExerciseProgression]:
        """Get weight progression for an exercise."""
        pass
