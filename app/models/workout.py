from pydantic import BaseModel
from typing import List, Optional

class Exercise(BaseModel):
    name: str
    sets: int
    reps: int
    weight: Optional[float] = None

class WorkoutLog(BaseModel):
    workout_id: str
    user_id: str
    date: str
    exercises: List[Exercise]

class WorkoutLogCreate(BaseModel):
    date: str
    exercises: List[Exercise]
