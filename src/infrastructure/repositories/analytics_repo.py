from datetime import datetime, timedelta, UTC
from typing import List
from sqlalchemy import select, func, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.repositories import AnalyticsRepository
from src.domain.value_objects import ExerciseProgression, AnalyticsSummary, WorkloadData, PersonalRecord
from src.infrastructure.db.models import WorkoutSessionModel, WorkoutExerciseModel, WorkoutSetModel, ExerciseModel

class SQLAlchemyAnalyticsRepository(AnalyticsRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_exercise_progression(self, user_id: int, exercise_id: int) -> List[ExerciseProgression]:
        stmt = (
            select(
                WorkoutSessionModel.start_time,
                func.max(WorkoutSetModel.weight).label("max_weight"),
                func.sum(WorkoutSetModel.weight * WorkoutSetModel.reps).label("total_volume")
            )
            .join(WorkoutExerciseModel, WorkoutSessionModel.id == WorkoutExerciseModel.session_id)
            .join(WorkoutSetModel, WorkoutExerciseModel.id == WorkoutSetModel.workout_exercise_id)
            .where(WorkoutSessionModel.user_id == user_id)
            .where(WorkoutExerciseModel.exercise_id == exercise_id)
            .where(WorkoutSetModel.is_warmup == False)
            .group_by(WorkoutSessionModel.id)
            .order_by(WorkoutSessionModel.start_time)
        )

        result = await self.session.execute(stmt)
        return [
            ExerciseProgression(
                date=row.start_time,
                max_weight=row.max_weight,
                total_volume=row.total_volume
            )
            for row in result.all()
        ]

    async def get_summary(self, user_id: int) -> AnalyticsSummary:
        # Total volume
        total_vol_stmt = (
            select(func.sum(WorkoutSetModel.weight * WorkoutSetModel.reps))
            .join(WorkoutExerciseModel, WorkoutSetModel.workout_exercise_id == WorkoutExerciseModel.id)
            .join(WorkoutSessionModel, WorkoutExerciseModel.session_id == WorkoutSessionModel.id)
            .where(WorkoutSessionModel.user_id == user_id)
            .where(WorkoutSetModel.is_warmup == False)
        )
        total_volume = (await self.session.execute(total_vol_stmt)).scalar() or 0.0

        # Workouts count
        workouts_cnt_stmt = (
            select(func.count(WorkoutSessionModel.id))
            .where(WorkoutSessionModel.user_id == user_id)
        )
        workouts_count = (await self.session.execute(workouts_cnt_stmt)).scalar() or 0

        # Last week volume change
        now = datetime.now(UTC)
        start_of_current_week = now - timedelta(days=7)
        start_of_last_week = now - timedelta(days=14)

        current_week_vol_stmt = (
            select(func.sum(WorkoutSetModel.weight * WorkoutSetModel.reps))
            .join(WorkoutExerciseModel, WorkoutSetModel.workout_exercise_id == WorkoutExerciseModel.id)
            .join(WorkoutSessionModel, WorkoutExerciseModel.session_id == WorkoutSessionModel.id)
            .where(WorkoutSessionModel.user_id == user_id)
            .where(WorkoutSessionModel.start_time >= start_of_current_week)
            .where(WorkoutSetModel.is_warmup == False)
        )
        current_week_volume = (await self.session.execute(current_week_vol_stmt)).scalar() or 0.0

        last_week_vol_stmt = (
            select(func.sum(WorkoutSetModel.weight * WorkoutSetModel.reps))
            .join(WorkoutExerciseModel, WorkoutSetModel.workout_exercise_id == WorkoutExerciseModel.id)
            .join(WorkoutSessionModel, WorkoutExerciseModel.session_id == WorkoutSessionModel.id)
            .where(WorkoutSessionModel.user_id == user_id)
            .where(WorkoutSessionModel.start_time >= start_of_last_week)
            .where(WorkoutSessionModel.start_time < start_of_current_week)
            .where(WorkoutSetModel.is_warmup == False)
        )
        last_week_volume = (await self.session.execute(last_week_vol_stmt)).scalar() or 0.0

        if last_week_volume > 0:
            change_percent = ((current_week_volume - last_week_volume) / last_week_volume) * 100
        else:
            change_percent = 100.0 if current_week_volume > 0 else 0.0

        # Records count
        records_stmt = (
            select(func.count(func.distinct(WorkoutExerciseModel.exercise_id)))
        )
        # This is a bit simplified, usually "records" means number of times user hit personal best
        # Let's count how many exercises have at least one record (set)
        records_count = (await self.session.execute(
             select(func.count(func.distinct(WorkoutExerciseModel.exercise_id)))
             .join(WorkoutSessionModel, WorkoutExerciseModel.session_id == WorkoutSessionModel.id)
             .where(WorkoutSessionModel.user_id == user_id)
        )).scalar() or 0

        return AnalyticsSummary(
            total_volume=total_volume,
            workouts_count=workouts_count,
            last_week_volume_change_percent=round(change_percent, 2),
            records_count=records_count
        )

    async def get_workload(self, user_id: int, period: str) -> List[WorkloadData]:
        from datetime import date as py_date
        days = 7 if period == "week" else 30
        start_date = datetime.now(UTC) - timedelta(days=days)

        stmt = (
            select(
                func.date(WorkoutSessionModel.start_time).label("date"),
                func.sum(WorkoutSetModel.weight * WorkoutSetModel.reps).label("volume")
            )
            .join(WorkoutExerciseModel, WorkoutSessionModel.id == WorkoutExerciseModel.session_id)
            .join(WorkoutSetModel, WorkoutExerciseModel.id == WorkoutSetModel.workout_exercise_id)
            .where(WorkoutSessionModel.user_id == user_id)
            .where(WorkoutSessionModel.start_time >= start_date)
            .where(WorkoutSetModel.is_warmup == False)
            .group_by(func.date(WorkoutSessionModel.start_time))
            .order_by(func.date(WorkoutSessionModel.start_time))
        )

        result = await self.session.execute(stmt)

        # Fill missing dates with 0 volume
        workload_map = {}
        for row in result.all():
            d_val = row.date
            if isinstance(d_val, str):
                d_val = py_date.fromisoformat(d_val)
            elif isinstance(d_val, datetime):
                d_val = d_val.date()
            workload_map[d_val] = row.volume

        full_data = []
        for i in range(days):
            d = (start_date + timedelta(days=i+1)).date()
            full_data.append(WorkloadData(date=d, volume=workload_map.get(d, 0.0)))

        return full_data

    async def get_records(self, user_id: int) -> List[PersonalRecord]:
        from datetime import date as py_date
        # Subquery to find max weight per exercise
        max_weights_subquery = (
            select(
                WorkoutExerciseModel.exercise_id,
                func.max(WorkoutSetModel.weight).label("max_weight")
            )
            .join(WorkoutSetModel, WorkoutExerciseModel.id == WorkoutSetModel.workout_exercise_id)
            .join(WorkoutSessionModel, WorkoutExerciseModel.session_id == WorkoutSessionModel.id)
            .where(WorkoutSessionModel.user_id == user_id)
            .where(WorkoutSetModel.is_warmup == False)
            .group_by(WorkoutExerciseModel.exercise_id)
        ).subquery()

        # Join back to get the date of the record (first time they hit that max weight)
        stmt = (
            select(
                ExerciseModel.name,
                max_weights_subquery.c.max_weight,
                func.min(func.date(WorkoutSessionModel.start_time)).label("date")
            )
            .join(max_weights_subquery, ExerciseModel.id == max_weights_subquery.c.exercise_id)
            .join(WorkoutExerciseModel, ExerciseModel.id == WorkoutExerciseModel.exercise_id)
            .join(WorkoutSessionModel, WorkoutExerciseModel.session_id == WorkoutSessionModel.id)
            .join(WorkoutSetModel, WorkoutExerciseModel.id == WorkoutSetModel.workout_exercise_id)
            .where(WorkoutSessionModel.user_id == user_id)
            .where(WorkoutSetModel.weight == max_weights_subquery.c.max_weight)
            .group_by(ExerciseModel.name, max_weights_subquery.c.max_weight)
        )

        result = await self.session.execute(stmt)
        records = []
        for row in result.all():
            d_val = row.date
            if isinstance(d_val, str):
                d_val = py_date.fromisoformat(d_val)
            elif isinstance(d_val, datetime):
                d_val = d_val.date()

            records.append(PersonalRecord(
                exercise_name=row.name,
                weight=row.max_weight,
                date=d_val
            ))
        return records
