import uuid
from fastapi import APIRouter, Depends
from app.models.goals import GoalCreate
from app.services.db_service import put_item, query_items, delete_item, update_item
from app.utils.jwt import get_current_user

router = APIRouter()

@router.post("")
def create_goal(body: GoalCreate, user_id: str = Depends(get_current_user)):
    goal_id = str(uuid.uuid4())
    item = {
        "user_id": user_id,
        "sk": f"GOAL#{goal_id}",
        "goal_id": goal_id,
        "type": body.type.value,
        "target_value": str(body.target_value),
    }
    put_item(item)
    return item

@router.get("")
def list_goals(user_id: str = Depends(get_current_user)):
    return query_items(user_id, "GOAL#")

@router.put("/{goal_id}")
def update_goal(goal_id: str, target_value: float, user_id: str = Depends(get_current_user)):
    update_item(user_id, f"GOAL#{goal_id}", "SET target_value = :v", {":v": str(target_value)})
    return {"goal_id": goal_id, "target_value": target_value}

@router.delete("/{goal_id}")
def delete_goal(goal_id: str, user_id: str = Depends(get_current_user)):
    delete_item(user_id, f"GOAL#{goal_id}")
    return {"deleted": goal_id}

@router.get("/progress")
def goals_progress(user_id: str = Depends(get_current_user)):
    goals = query_items(user_id, "GOAL#")
    metrics = query_items(user_id, "METRIC#")
    nutrition = query_items(user_id, "NUTRITION#")
    workouts = query_items(user_id, "WORKOUT#")

    latest_weight, today_steps = None, 0
    if metrics:
        latest = sorted(metrics, key=lambda x: x.get("date", ""), reverse=True)[0]
        latest_weight = float(latest.get("weight_kg", 0) or 0)
        today_steps = int(latest.get("steps", 0) or 0)

    today_calories = sum(float(n.get("calories", 0)) for n in nutrition)

    result = []
    for g in goals:
        gtype = g.get("type")
        current = None
        if gtype == "weight":
            current = latest_weight
        elif gtype == "calories":
            current = today_calories
        elif gtype == "workouts":
            current = len(workouts)
        elif gtype == "steps":
            current = today_steps
        result.append({**g, "current_value": current})
    return result
