from pydantic import BaseModel
from enum import Enum

class GoalType(str, Enum):
    weight = "weight"
    calories = "calories"
    workouts = "workouts"
    steps = "steps"

class Goal(BaseModel):
    goal_id: str
    user_id: str
    type: GoalType
    target_value: float

class GoalCreate(BaseModel):
    type: GoalType
    target_value: float
