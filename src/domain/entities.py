from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import List, Optional
from enum import Enum

class WorkoutStatus(str, Enum):
    """
    Status of a workout session.
    """
    ACTIVE = "active"
    COMPLETED = "completed"

@dataclass
class User:
    """
    User entity representing a person using the tracker.

    Attributes:
        id (Optional[int]): Primary key.
        telegram_id (int): Unique Telegram ID.
        username (Optional[str]): Telegram username.
        created_at (datetime): Registration timestamp.
    """
    id: Optional[int]
    telegram_id: int
    username: Optional[str]
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

@dataclass
class Exercise:
    """
    Exercise entity representing a specific physical activity.

    Attributes:
        id (Optional[int]): Primary key.
        name (str): Name of the exercise.
        primary_muscle_group (str): Main muscle group targeted.
        secondary_muscle_groups (List[str]): Other muscle groups involved.
        description (Optional[str]): Detailed instructions or info.
        media_url (Optional[str]): URL to image/video.
        comment (Optional[str]): Personal notes.
    """
    id: Optional[int]
    name: str
    primary_muscle_group: str
    secondary_muscle_groups: List[str]
    description: Optional[str]
    media_url: Optional[str]
    comment: Optional[str]

@dataclass
class TrainingProgram:
    """
    Training Program entity representing a collection of plans.

    Attributes:
        id (Optional[int]): Primary key.
        user_id (int): Owner's ID.
        name (str): Program name.
        description (Optional[str]): Program details.
    """
    id: Optional[int]
    user_id: int
    name: str
    description: Optional[str]

@dataclass
class TrainingPlan:
    """
    Training Plan entity representing a single workout routine.

    Attributes:
        id (Optional[int]): Primary key.
        program_id (int): Parent program ID.
        name (str): Plan name.
        day_of_week (Optional[int]): Suggested day (0-6).
    """
    id: Optional[int]
    program_id: int
    name: str
    day_of_week: Optional[int]

@dataclass
class PlanExercise:
    """
    Association entity between a Plan and an Exercise with target goals.

    Attributes:
        plan_id (int): Plan ID.
        exercise_id (int): Exercise ID.
        target_sets (int): Number of sets planned.
        target_reps (int): Number of reps planned per set.
    """
    plan_id: int
    exercise_id: int
    target_sets: int
    target_reps: int

@dataclass
class WorkoutSession:
    """
    Workout Session entity representing a single workout event.

    Attributes:
        id (Optional[int]): Primary key.
        user_id (int): User's ID.
        plan_id (Optional[int]): ID of the plan followed (if any).
        start_time (datetime): When the workout started.
        end_time (Optional[datetime]): When the workout ended.
        status (WorkoutStatus): Current status (active/completed).
    """
    id: Optional[int]
    user_id: int
    plan_id: Optional[int]
    start_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    end_time: Optional[datetime] = None
    status: WorkoutStatus = WorkoutStatus.ACTIVE

@dataclass
class WorkoutExercise:
    """
    Workout Exercise entity representing an exercise performed during a session.

    Attributes:
        id (Optional[int]): Primary key.
        session_id (int): Session ID.
        exercise_id (int): Exercise ID.
        order (int): Order in the workout.
    """
    id: Optional[int]
    session_id: int
    exercise_id: int
    order: int

@dataclass
class WorkoutSet:
    """
    Workout Set entity representing a single set performed.

    Attributes:
        id (Optional[int]): Primary key.
        workout_exercise_id (int): Workout Exercise ID.
        reps (int): Number of repetitions performed.
        weight (float): Weight used in kilograms.
        time_spent_seconds (Optional[int]): Duration of the set.
        rest_time_seconds (Optional[int]): Rest duration after the set.
    """
    id: Optional[int]
    workout_exercise_id: int
    reps: int
    weight: float
    time_spent_seconds: Optional[int]
    rest_time_seconds: Optional[int]
