from dataclasses import dataclass
from datetime import datetime, date

@dataclass
class ExerciseProgression:
    date: datetime
    max_weight: float
    total_volume: float

@dataclass
class AnalyticsSummary:
    total_volume: float
    workouts_count: int
    last_week_volume_change_percent: float
    records_count: int

@dataclass
class WorkloadData:
    date: date
    volume: float

@dataclass
class PersonalRecord:
    exercise_name: str
    weight: float
    date: date
