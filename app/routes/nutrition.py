import uuid
from fastapi import APIRouter, Depends
from typing import Optional
from app.models.nutrition import NutritionCreate
from app.services.db_service import put_item, query_items, delete_item
from app.utils.jwt import get_current_user

router = APIRouter()

@router.post("")
def log_nutrition(body: NutritionCreate, user_id: str = Depends(get_current_user)):
    entry_id = str(uuid.uuid4())
    item = {
        "user_id": user_id,
        "sk": f"NUTRITION#{entry_id}",
        "entry_id": entry_id,
        "date": body.date,
        "calories": str(body.calories),
        "protein": str(body.protein),
        "carbs": str(body.carbs),
        "fat": str(body.fat),
        "water_ml": str(body.water_ml) if body.water_ml else "0",
    }
    put_item(item)
    return item

@router.get("")
def list_nutrition(user_id: str = Depends(get_current_user), date: Optional[str] = None):
    items = query_items(user_id, "NUTRITION#")
    if date:
        items = [i for i in items if i.get("date") == date]
    return items

@router.get("/summary")
def nutrition_summary(date: str, user_id: str = Depends(get_current_user)):
    items = [i for i in query_items(user_id, "NUTRITION#") if i.get("date") == date]
    totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "water_ml": 0}
    for i in items:
        for key in totals:
            totals[key] += float(i.get(key, 0))
    return totals

@router.delete("/{entry_id}")
def delete_nutrition(entry_id: str, user_id: str = Depends(get_current_user)):
    delete_item(user_id, f"NUTRITION#{entry_id}")
    return {"deleted": entry_id}
