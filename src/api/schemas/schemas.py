from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from src.domain.entities import WorkoutStatus

class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None

class UserRead(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ExerciseBase(BaseModel):
    name: str
    primary_muscle_group: str
    secondary_muscle_groups: List[str] = []
    description: Optional[str] = None
    media_url: Optional[str] = None
    comment: Optional[str] = None

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    primary_muscle_group: Optional[str] = None
    secondary_muscle_groups: Optional[List[str]] = None
    description: Optional[str] = None
    media_url: Optional[str] = None
    comment: Optional[str] = None

class ExerciseRead(ExerciseBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class TrainingProgramBase(BaseModel):
    name: str
    description: Optional[str] = None

class TrainingProgramCreate(TrainingProgramBase):
    user_id: int

class TrainingProgramUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class TrainingProgramRead(TrainingProgramBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)

class TrainingPlanBase(BaseModel):
    name: str
    day_of_week: Optional[int] = None

class TrainingPlanCreate(TrainingPlanBase):
    program_id: int

class TrainingPlanUpdate(BaseModel):
    name: Optional[str] = None
    day_of_week: Optional[int] = None

class TrainingPlanRead(TrainingPlanBase):
    id: int
    program_id: int
    model_config = ConfigDict(from_attributes=True)

class PlanExerciseBase(BaseModel):
    exercise_id: int
    target_sets: int
    target_reps: int

class PlanExerciseRead(PlanExerciseBase):
    plan_id: int
    model_config = ConfigDict(from_attributes=True)

class WorkoutSessionRead(BaseModel):
    id: int
    user_id: int
    plan_id: Optional[int]
    start_time: datetime
    end_time: Optional[datetime]
    status: WorkoutStatus
    model_config = ConfigDict(from_attributes=True)

class WorkoutSetCreate(BaseModel):
    reps: int
    weight: float
    time_spent_seconds: Optional[int] = None
    rest_time_seconds: Optional[int] = None

class WorkoutSetRead(WorkoutSetCreate):
    id: int
    workout_exercise_id: int
    model_config = ConfigDict(from_attributes=True)

class WorkoutExerciseRead(BaseModel):
    id: int
    session_id: int
    exercise_id: int
    order: int
    model_config = ConfigDict(from_attributes=True)

class ProgressionRead(BaseModel):
    date: datetime
    max_weight: float
    total_volume: float
