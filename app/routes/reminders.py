import uuid
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from app.models.reminder import ReminderCreate, ReminderUpdate
from app.services.db_service import put_item, get_item, query_items, delete_item
from app.utils.jwt import get_current_user

router = APIRouter()


@router.post("")
def create_reminder(body: ReminderCreate, user_id: str = Depends(get_current_user)):
    reminder_id = str(uuid.uuid4())
    item = {
        "user_id": user_id,
        "sk": f"REMINDER#{reminder_id}",
        "reminder_id": reminder_id,
        "title": body.title,
        "reminder_type": body.reminder_type,
        "message": body.message,
        "remind_at": body.remind_at,
        "recurring": body.recurring,
        "recurrence_pattern": body.recurrence_pattern,
        "is_active": body.is_active,
    }
    put_item(item)
    return item


@router.get("")
def list_reminders(
    user_id: str = Depends(get_current_user),
    is_active: Optional[bool] = None,
):
    items = query_items(user_id, "REMINDER#")
    if is_active is not None:
        items = [item for item in items if bool(item.get("is_active")) is is_active]
    return items


@router.get("/{reminder_id}")
def get_reminder(reminder_id: str, user_id: str = Depends(get_current_user)):
    item = get_item(user_id, f"REMINDER#{reminder_id}")
    if not item:
        raise HTTPException(status_code=404, detail="reminder not found")
    return item


@router.put("/{reminder_id}")
def update_reminder(
    reminder_id: str,
    body: ReminderUpdate,
    user_id: str = Depends(get_current_user),
):
    item = get_item(user_id, f"REMINDER#{reminder_id}")
    if not item:
        raise HTTPException(status_code=404, detail="reminder not found")

    updates = body.model_dump(exclude_unset=True)
    item.update(updates)
    put_item(item)
    return item


@router.delete("/{reminder_id}")
def delete_reminder(reminder_id: str, user_id: str = Depends(get_current_user)):
    delete_item(user_id, f"REMINDER#{reminder_id}")
    return {"deleted": reminder_id}
