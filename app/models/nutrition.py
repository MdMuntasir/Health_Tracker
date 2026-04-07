from pydantic import BaseModel
from typing import Optional

class NutritionEntry(BaseModel):
    entry_id: str
    user_id: str
    date: str
    calories: float
    protein: float
    carbs: float
    fat: float
    water_ml: Optional[float] = None

class NutritionCreate(BaseModel):
    date: str
    calories: float
    protein: float
    carbs: float
    fat: float
    water_ml: Optional[float] = None
