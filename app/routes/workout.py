import uuid
from fastapi import APIRouter, HTTPException, Depends
from app.models.workout import WorkoutLogCreate
from app.services.db_service import put_item, get_item, query_items, delete_item
from app.utils.jwt import get_current_user

router = APIRouter()

@router.post("")
def create_workout(body: WorkoutLogCreate, user_id: str = Depends(get_current_user)):
    workout_id = str(uuid.uuid4())
    item = {
        "user_id": user_id,
        "sk": f"WORKOUT#{workout_id}",
        "workout_id": workout_id,
        "date": body.date,
        "exercises": [e.dict() for e in body.exercises],
    }
    put_item(item)
    return item

@router.get("")
def list_workouts(user_id: str = Depends(get_current_user)):
    return query_items(user_id, "WORKOUT#")

@router.get("/{workout_id}")
def get_workout(workout_id: str, user_id: str = Depends(get_current_user)):
    item = get_item(user_id, f"WORKOUT#{workout_id}")
    if not item:
        raise HTTPException(status_code=404, detail="workout not found")
    return item

@router.delete("/{workout_id}")
def delete_workout(workout_id: str, user_id: str = Depends(get_current_user)):
    delete_item(user_id, f"WORKOUT#{workout_id}")
    return {"deleted": workout_id}
