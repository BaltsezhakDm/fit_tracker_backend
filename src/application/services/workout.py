from datetime import datetime, UTC
from typing import List, Optional, Any
from src.domain.entities import WorkoutSession, WorkoutExercise, WorkoutSet, WorkoutStatus
from src.domain.repositories import (
    WorkoutSessionRepository, WorkoutExerciseRepository, WorkoutSetRepository
)

class WorkoutService:
    """
    Service for managing active workout sessions and tracking progress.
    """
    def __init__(self,
                 session_repo: WorkoutSessionRepository,
                 workout_exercise_repo: WorkoutExerciseRepository,
                 workout_set_repo: WorkoutSetRepository):
        """
        Initialize WorkoutService.

        Args:
            session_repo (WorkoutSessionRepository): Repository for workout sessions.
            workout_exercise_repo (WorkoutExerciseRepository): Repository for workout exercises.
            workout_set_repo (WorkoutSetRepository): Repository for sets.
        """
        self.session_repo = session_repo
        self.workout_exercise_repo = workout_exercise_repo
        self.workout_set_repo = workout_set_repo

    async def start_workout(self, user_id: int, plan_id: Optional[int] = None) -> WorkoutSession:
        """
        Start a new workout session for a user.

        Args:
            user_id (int): ID of the user.
            plan_id (Optional[int]): ID of the plan being followed.

        Returns:
            WorkoutSession: The started (or already active) session.
        """
        active_session = await self.session_repo.get_active_session_by_user_id(user_id)
        if active_session:
            return active_session

        session = WorkoutSession(id=None, user_id=user_id, plan_id=plan_id)
        return await self.session_repo.create(session)

    async def add_exercise_to_workout(self, session_id: Any, exercise_id: int, technique_details: dict = None) -> WorkoutExercise:
        """
        Add an exercise to an active session.

        Args:
            session_id (Any): ID of the active session.
            exercise_id (int): ID of the exercise.
            technique_details (dict): Technique variations or notes.

        Returns:
            WorkoutExercise: The added workout exercise entry.
        """
        if technique_details is None:
            technique_details = {}
        existing_exercises = await self.workout_exercise_repo.get_by_session_id(session_id)
        order = len(existing_exercises) + 1
        workout_exercise = WorkoutExercise(
            id=None, session_id=session_id, exercise_id=exercise_id,
            order=order, technique_details=technique_details
        )
        return await self.workout_exercise_repo.create(workout_exercise)

    async def add_set(self, workout_exercise_id: Any, reps: int, weight: float,
                      time_spent_seconds: Optional[int] = None,
                      rest_time_seconds: Optional[int] = None,
                      is_warmup: bool = False,
                      rpe: Optional[int] = None,
                      rir: Optional[int] = None) -> WorkoutSet:
        """
        Record a performed set for a workout exercise.

        Args:
            workout_exercise_id (Any): ID of the workout exercise.
            reps (int): Repetitions performed.
            weight (float): Weight used.
            time_spent_seconds (Optional[int]): Duration of the set.
            rest_time_seconds (Optional[int]): Rest after the set.

        Returns:
            WorkoutSet: The recorded set entry.
        """
        workout_set = WorkoutSet(
            id=None,
            workout_exercise_id=workout_exercise_id,
            reps=reps,
            weight=weight,
            time_spent_seconds=time_spent_seconds,
            rest_time_seconds=rest_time_seconds,
            is_warmup=is_warmup,
            rpe=rpe,
            rir=rir
        )
        return await self.workout_set_repo.create(workout_set)

    async def hot_swap_exercise(self, workout_exercise_id: Any, new_exercise_id: int) -> WorkoutExercise:
        """
        Replace an exercise in the middle of a workout.

        Args:
            workout_exercise_id (Any): Current workout exercise ID.
            new_exercise_id (int): ID of the replacement exercise.

        Returns:
            WorkoutExercise: The updated workout exercise entry.
        """
        workout_exercise = await self.workout_exercise_repo.get_by_id(workout_exercise_id)
        if not workout_exercise:
            raise ValueError("Workout exercise not found")

        workout_exercise.exercise_id = new_exercise_id
        return await self.workout_exercise_repo.update(workout_exercise)

    async def complete_workout(self, session_id: Any) -> WorkoutSession:
        """
        Finalize a workout session.

        Args:
            session_id (Any): ID of the session to complete.

        Returns:
            WorkoutSession: The completed session.
        """
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found")

        session.end_time = datetime.now(UTC)
        session.status = WorkoutStatus.COMPLETED
        return await self.session_repo.update(session)

    async def get_workout_history(self, user_id: int) -> List[WorkoutSession]:
        """
        Get all past workout sessions for a user.

        Args:
            user_id (int): User ID.

        Returns:
            List[WorkoutSession]: List of sessions.
        """
        return await self.session_repo.get_history_by_user_id(user_id)

    async def delete_workout_session(self, session_id: Any) -> None:
        """
        Delete a workout session from history.

        Args:
            session_id (Any): ID of the session to delete.
        """
        await self.session_repo.delete(session_id)

    async def get_session_exercises(self, session_id: Any) -> List[WorkoutExercise]:
        """
        Get all exercises performed in a specific session.

        Args:
            session_id (Any): Session ID.

        Returns:
            List[WorkoutExercise]: List of workout exercises.
        """
        return await self.workout_exercise_repo.get_by_session_id(session_id)

    async def get_workout_exercise_sets(self, workout_exercise_id: Any) -> List[WorkoutSet]:
        """
        Get all sets for a specific workout exercise.

        Args:
            workout_exercise_id (Any): Workout Exercise ID.

        Returns:
            List[WorkoutSet]: List of sets.
        """
        return await self.workout_set_repo.get_by_workout_exercise_id(workout_exercise_id)
