from pydantic import BaseModel
from typing import Literal, Optional

class MetricEntry(BaseModel):
    metric_id: str
    user_id: str
    date: str
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    bmi: Optional[float] = None
    sleep_hours: Optional[float] = None
    sleep_quality: Optional[Literal["poor", "fair", "good", "excellent"]] = None
    steps: Optional[int] = None

class MetricCreate(BaseModel):
    date: str
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    bmi: Optional[float] = None
    sleep_hours: Optional[float] = None
    sleep_quality: Optional[Literal["poor", "fair", "good", "excellent"]] = None
    steps: Optional[int] = None
