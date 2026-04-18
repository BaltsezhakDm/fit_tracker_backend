from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import List, Optional, Dict, Any
from enum import Enum
from uuid import UUID

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
        biomechanics_tags (List[str]): Tags for anthropometric adaptation.
    """
    id: Optional[int]
    name: str
    primary_muscle_group: str
    secondary_muscle_groups: List[str]
    description: Optional[str]
    media_url: Optional[str]
    comment: Optional[str]
    biomechanics_tags: List[str] = field(default_factory=list)

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
        id (Optional[UUID]): Primary key.
        user_id (int): User's ID.
        plan_id (Optional[int]): ID of the plan followed (if any).
        start_time (datetime): When the workout started.
        end_time (Optional[datetime]): When the workout ended.
        status (WorkoutStatus): Current status (active/completed).
    """
    id: Optional[UUID]
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
        id (Optional[UUID]): Primary key.
        session_id (UUID): Session ID.
        exercise_id (int): Exercise ID.
        order (int): Order in the workout.
        technique_details (Dict[str, Any]): Technique variations or notes.
    """
    id: Optional[UUID]
    session_id: UUID
    exercise_id: int
    order: int
    technique_details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkoutSet:
    """
    Workout Set entity representing a single set performed.

    Attributes:
        id (Optional[UUID]): Primary key.
        workout_exercise_id (UUID): Workout Exercise ID.
        reps (int): Number of repetitions performed.
        weight (float): Weight used in kilograms.
        time_spent_seconds (Optional[int]): Duration of the set.
        rest_time_seconds (Optional[int]): Rest duration after the set.
        is_warmup (bool): Whether the set is a warmup.
        rpe (Optional[int]): Rated Perceived Exertion (1-10).
        rir (Optional[int]): Reps in Reserve.
    """
    id: Optional[UUID]
    workout_exercise_id: UUID
    reps: int
    weight: float
    time_spent_seconds: Optional[int]
    rest_time_seconds: Optional[int]
    is_warmup: bool = False
    rpe: Optional[int] = None
    rir: Optional[int] = None

@dataclass
class BlacklistedExercise:
    """
    Entity for blacklisted exercises per user.
    """
    user_id: int
    exercise_id: int
