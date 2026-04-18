from dataclasses import dataclass
from datetime import datetime

@dataclass
class ExerciseProgression:
    date: datetime
    max_weight: float
    total_volume: float
