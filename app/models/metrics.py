from pydantic import BaseModel
from typing import Optional

class MetricEntry(BaseModel):
    metric_id: str
    user_id: str
    date: str
    weight_kg: Optional[float] = None
    bmi: Optional[float] = None
    sleep_hours: Optional[float] = None
    steps: Optional[int] = None

class MetricCreate(BaseModel):
    date: str
    weight_kg: Optional[float] = None
    bmi: Optional[float] = None
    sleep_hours: Optional[float] = None
    steps: Optional[int] = None
