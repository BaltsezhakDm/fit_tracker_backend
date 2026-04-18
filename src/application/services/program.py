from typing import List, Optional
from src.domain.entities import TrainingProgram, TrainingPlan, PlanExercise
from src.domain.repositories import TrainingProgramRepository, TrainingPlanRepository, PlanExerciseRepository

class ProgramService:
    """
    Service for managing training programs and their constituent plans.
    """
    def __init__(self,
                 program_repo: TrainingProgramRepository,
                 plan_repo: TrainingPlanRepository,
                 plan_exercise_repo: PlanExerciseRepository):
        """
        Initialize ProgramService.

        Args:
            program_repo (TrainingProgramRepository): Repository for programs.
            plan_repo (TrainingPlanRepository): Repository for plans.
            plan_exercise_repo (PlanExerciseRepository): Repository for plan-exercise associations.
        """
        self.program_repo = program_repo
        self.plan_repo = plan_repo
        self.plan_exercise_repo = plan_exercise_repo

    async def create_program(self, user_id: int, name: str, description: Optional[str] = None) -> TrainingProgram:
        """
        Create a new training program for a user.

        Args:
            user_id (int): ID of the user owning the program.
            name (str): Name of the program.
            description (Optional[str]): Optional program description.

        Returns:
            TrainingProgram: Created program entity.
        """
        program = TrainingProgram(id=None, user_id=user_id, name=name, description=description)
        return await self.program_repo.create(program)

    async def add_plan_to_program(self, program_id: int, name: str, day_of_week: Optional[int] = None) -> TrainingPlan:
        """
        Add a training plan to an existing program.

        Args:
            program_id (int): ID of the parent program.
            name (str): Name of the plan.
            day_of_week (Optional[int]): Suggested day of the week (0-6).

        Returns:
            TrainingPlan: Created plan entity.
        """
        plan = TrainingPlan(id=None, program_id=program_id, name=name, day_of_week=day_of_week)
        return await self.plan_repo.create(plan)

    async def add_exercise_to_plan(self, plan_id: int, exercise_id: int, target_sets: int, target_reps: int) -> None:
        """
        Add an exercise with target sets and reps to a plan.

        Args:
            plan_id (int): ID of the plan.
            exercise_id (int): ID of the exercise.
            target_sets (int): Number of sets.
            target_reps (int): Number of reps per set.
        """
        plan_exercise = PlanExercise(plan_id=plan_id, exercise_id=exercise_id, target_sets=target_sets, target_reps=target_reps)
        await self.plan_exercise_repo.add_exercise_to_plan(plan_exercise)

    async def get_user_programs(self, user_id: int) -> List[TrainingProgram]:
        """
        Get all training programs belonging to a user.

        Args:
            user_id (int): User ID.

        Returns:
            List[TrainingProgram]: List of programs.
        """
        return await self.program_repo.get_by_user_id(user_id)

    async def get_program_plans(self, program_id: int) -> List[TrainingPlan]:
        """
        Get all training plans within a program.

        Args:
            program_id (int): Program ID.

        Returns:
            List[TrainingPlan]: List of plans.
        """
        return await self.plan_repo.get_by_program_id(program_id)

    async def get_plan_exercises(self, plan_id: int) -> List[PlanExercise]:
        """
        Get all exercises scheduled for a specific plan.

        Args:
            plan_id (int): Plan ID.

        Returns:
            List[PlanExercise]: List of plan-exercise associations.
        """
        return await self.plan_exercise_repo.get_exercises_by_plan_id(plan_id)

    async def update_program(self, program_id: int, name: Optional[str] = None, description: Optional[str] = None) -> Optional[TrainingProgram]:
        """
        Update program details.

        Args:
            program_id (int): ID of the program.
            name (Optional[str]): New name.
            description (Optional[str]): New description.

        Returns:
            Optional[TrainingProgram]: Updated program or None if not found.
        """
        program = await self.program_repo.get_by_id(program_id)
        if not program:
            return None
        if name is not None:
            program.name = name
        if description is not None:
            program.description = description
        return await self.program_repo.update(program)

    async def delete_program(self, program_id: int) -> None:
        """
        Delete a training program.

        Args:
            program_id (int): ID of the program.
        """
        await self.program_repo.delete(program_id)

    async def update_plan(self, plan_id: int, name: Optional[str] = None, day_of_week: Optional[int] = None) -> Optional[TrainingPlan]:
        """
        Update training plan details.

        Args:
            plan_id (int): ID of the plan.
            name (Optional[str]): New name.
            day_of_week (Optional[int]): New day of week.

        Returns:
            Optional[TrainingPlan]: Updated plan or None if not found.
        """
        plan = await self.plan_repo.get_by_id(plan_id)
        if not plan:
            return None
        if name is not None:
            plan.name = name
        if day_of_week is not None:
            plan.day_of_week = day_of_week
        return await self.plan_repo.update(plan)

    async def delete_plan(self, plan_id: int) -> None:
        """
        Delete a training plan.

        Args:
            plan_id (int): ID of the plan.
        """
        await self.plan_repo.delete(plan_id)
