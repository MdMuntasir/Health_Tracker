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


class ExerciseLibraryItem(BaseModel):
    exercise_id: str
    name: str
    category: str
    muscle_group: str
    equipment: Optional[str] = None


class WorkoutPlanDay(BaseModel):
    day_of_week: str
    exercises: List[Exercise]


class WorkoutPlanCreate(BaseModel):
    name: str
    week_start: Optional[str] = None
    days: List[WorkoutPlanDay]


class WorkoutPlanUpdate(BaseModel):
    name: Optional[str] = None
    week_start: Optional[str] = None
    days: Optional[List[WorkoutPlanDay]] = None
