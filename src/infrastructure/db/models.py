from datetime import datetime, UTC
from typing import List, Optional, Any, Dict
import uuid6
from sqlalchemy import String, ForeignKey, JSON, Integer, Float, DateTime, Boolean, Enum as SQLEnum, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from src.domain.entities import WorkoutStatus

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    """
    pass

class UserModel(Base):
    """
    SQLAlchemy model for Users table.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

class ExerciseModel(Base):
    """
    SQLAlchemy model for Exercises table.
    """
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    primary_muscle_group: Mapped[str] = mapped_column(String(100))
    secondary_muscle_groups: Mapped[list] = mapped_column(JSON, default=list)
    description: Mapped[Optional[str]] = mapped_column(String)
    media_url: Mapped[Optional[str]] = mapped_column(String)
    comment: Mapped[Optional[str]] = mapped_column(String)
    biomechanics_tags: Mapped[list] = mapped_column(JSON, default=list)

class TrainingProgramModel(Base):
    """
    SQLAlchemy model for Training Programs table.
    """
    __tablename__ = "training_programs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String)

class TrainingPlanModel(Base):
    """
    SQLAlchemy model for Training Plans table.
    """
    __tablename__ = "training_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("training_programs.id"))
    name: Mapped[str] = mapped_column(String(255))
    day_of_week: Mapped[Optional[int]] = mapped_column()

class PlanExerciseModel(Base):
    """
    SQLAlchemy model for Plan Exercises association table.
    """
    __tablename__ = "plan_exercises"

    plan_id: Mapped[int] = mapped_column(ForeignKey("training_plans.id"), primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), primary_key=True)
    target_sets: Mapped[int] = mapped_column()
    target_reps: Mapped[int] = mapped_column()

class WorkoutSessionModel(Base):
    """
    SQLAlchemy model for Workout Sessions table.
    """
    __tablename__ = "workout_sessions"

    id: Mapped[uuid6.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    plan_id: Mapped[Optional[int]] = mapped_column(ForeignKey("training_plans.id"), nullable=True)
    start_time: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    end_time: Mapped[Optional[datetime]] = mapped_column()
    status: Mapped[WorkoutStatus] = mapped_column(SQLEnum(WorkoutStatus), default=WorkoutStatus.ACTIVE)

class WorkoutExerciseModel(Base):
    """
    SQLAlchemy model for Workout Exercises table.
    """
    __tablename__ = "workout_exercises"

    id: Mapped[uuid6.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)
    session_id: Mapped[uuid6.UUID] = mapped_column(ForeignKey("workout_sessions.id"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))
    order: Mapped[int] = mapped_column()
    technique_details: Mapped[dict] = mapped_column(JSON, default=dict)

class WorkoutSetModel(Base):
    """
    SQLAlchemy model for Workout Sets table.
    """
    __tablename__ = "workout_sets"

    id: Mapped[uuid6.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7)
    workout_exercise_id: Mapped[uuid6.UUID] = mapped_column(ForeignKey("workout_exercises.id"))
    reps: Mapped[int] = mapped_column()
    weight: Mapped[float] = mapped_column(Float)
    time_spent_seconds: Mapped[Optional[int]] = mapped_column()
    rest_time_seconds: Mapped[Optional[int]] = mapped_column()
    is_warmup: Mapped[bool] = mapped_column(Boolean, default=False)
    rpe: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rir: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

class UserBlacklistedExerciseModel(Base):
    """
    SQLAlchemy model for User Blacklisted Exercises (Many-to-Many).
    """
    __tablename__ = "user_blacklisted_exercises"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), primary_key=True)
