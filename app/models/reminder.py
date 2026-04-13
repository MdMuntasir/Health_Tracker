from pydantic import BaseModel
from typing import Optional


class ReminderCreate(BaseModel):
    title: str
    reminder_type: str
    message: Optional[str] = None
    remind_at: Optional[str] = None
    recurring: bool = False
    recurrence_pattern: Optional[str] = None
    is_active: bool = True


class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    reminder_type: Optional[str] = None
    message: Optional[str] = None
    remind_at: Optional[str] = None
    recurring: Optional[bool] = None
    recurrence_pattern: Optional[str] = None
    is_active: Optional[bool] = None
