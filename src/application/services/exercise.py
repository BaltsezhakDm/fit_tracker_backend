from typing import List, Optional
from src.domain.entities import Exercise
from src.domain.repositories import ExerciseRepository

class ExerciseService:
    """
    Service for managing exercises knowledge base.
    """
    def __init__(self, exercise_repo: ExerciseRepository):
        """
        Initialize ExerciseService.

        Args:
            exercise_repo (ExerciseRepository): Repository for exercise data.
        """
        self.exercise_repo = exercise_repo

    async def create_exercise(self, name: str, primary_muscle_group: str,
                               secondary_muscle_groups: List[str],
                               description: Optional[str] = None,
                               media_url: Optional[str] = None,
                               comment: Optional[str] = None) -> Exercise:
        """
        Create a new exercise in the knowledge base.

        Args:
            name (str): Name of the exercise.
            primary_muscle_group (str): Primary muscle group targeted.
            secondary_muscle_groups (List[str]): List of secondary muscle groups.
            description (Optional[str]): Detailed description or instructions.
            media_url (Optional[str]): URL to media content.
            comment (Optional[str]): Personal or general comment.

        Returns:
            Exercise: The created exercise entity.
        """
        exercise = Exercise(
            id=None,
            name=name,
            primary_muscle_group=primary_muscle_group,
            secondary_muscle_groups=secondary_muscle_groups,
            description=description,
            media_url=media_url,
            comment=comment
        )
        return await self.exercise_repo.create(exercise)

    async def get_exercise(self, exercise_id: int) -> Optional[Exercise]:
        """
        Retrieve an exercise by its ID.

        Args:
            exercise_id (int): Unique ID of the exercise.

        Returns:
            Optional[Exercise]: Exercise entity if found, None otherwise.
        """
        return await self.exercise_repo.get_by_id(exercise_id)

    async def get_all_exercises(self) -> List[Exercise]:
        """
        Retrieve all exercises from the database.

        Returns:
            List[Exercise]: List of all exercises.
        """
        return await self.exercise_repo.get_all()

    async def update_exercise(self, exercise: Exercise) -> Exercise:
        """
        Update an existing exercise.

        Args:
            exercise (Exercise): Exercise entity with updated fields.

        Returns:
            Exercise: The updated exercise entity.
        """
        return await self.exercise_repo.update(exercise)

    async def delete_exercise(self, exercise_id: int) -> None:
        """
        Remove an exercise from the knowledge base.

        Args:
            exercise_id (int): ID of the exercise to delete.
        """
        await self.exercise_repo.delete(exercise_id)
