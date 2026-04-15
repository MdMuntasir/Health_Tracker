import uuid
from datetime import date, datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from app.models.workout import WorkoutLogCreate, WorkoutPlanCreate, WorkoutPlanUpdate
from app.services.db_service import put_item, get_item, query_items, delete_item
from app.utils.jwt import get_current_user

router = APIRouter()

EXERCISE_LIBRARY = [
    {"exercise_id": "bench-press", "name": "Bench Press", "category": "strength", "muscle_group": "chest", "equipment": "barbell"},
    {"exercise_id": "incline-dumbbell-press", "name": "Incline Dumbbell Press", "category": "strength", "muscle_group": "chest", "equipment": "dumbbell"},
    {"exercise_id": "squat", "name": "Squat", "category": "strength", "muscle_group": "legs", "equipment": "barbell"},
    {"exercise_id": "romanian-deadlift", "name": "Romanian Deadlift", "category": "strength", "muscle_group": "legs", "equipment": "barbell"},
    {"exercise_id": "lat-pulldown", "name": "Lat Pulldown", "category": "strength", "muscle_group": "back", "equipment": "machine"},
    {"exercise_id": "pull-up", "name": "Pull-up", "category": "strength", "muscle_group": "back", "equipment": "bodyweight"},
    {"exercise_id": "shoulder-press", "name": "Shoulder Press", "category": "strength", "muscle_group": "shoulders", "equipment": "dumbbell"},
    {"exercise_id": "lateral-raise", "name": "Lateral Raise", "category": "strength", "muscle_group": "shoulders", "equipment": "dumbbell"},
    {"exercise_id": "bicep-curl", "name": "Bicep Curl", "category": "strength", "muscle_group": "arms", "equipment": "dumbbell"},
    {"exercise_id": "tricep-pushdown", "name": "Tricep Pushdown", "category": "strength", "muscle_group": "arms", "equipment": "cable"},
    {"exercise_id": "plank", "name": "Plank", "category": "core", "muscle_group": "core", "equipment": "bodyweight"},
    {"exercise_id": "crunch", "name": "Crunch", "category": "core", "muscle_group": "core", "equipment": "bodyweight"},
    {"exercise_id": "running", "name": "Running", "category": "cardio", "muscle_group": "full-body", "equipment": "none"},
    {"exercise_id": "cycling", "name": "Cycling", "category": "cardio", "muscle_group": "legs", "equipment": "bike"},
]


def _parse_workout_date(raw_date: str):
    try:
        return datetime.strptime(raw_date, "%Y-%m-%d").date()
    except ValueError:
        return None


@router.get("/exercises")
def exercise_library(
    category: Optional[str] = None,
    muscle_group: Optional[str] = None,
    search: Optional[str] = None,
):
    items = EXERCISE_LIBRARY
    if category:
        items = [i for i in items if i["category"].lower() == category.lower()]
    if muscle_group:
        items = [i for i in items if i["muscle_group"].lower() == muscle_group.lower()]
    if search:
        q = search.lower()
        items = [i for i in items if q in i["name"].lower()]
    return items


@router.post("/plans")
def create_workout_plan(body: WorkoutPlanCreate, user_id: str = Depends(get_current_user)):
    plan_id = str(uuid.uuid4())
    item = {
        "user_id": user_id,
        "sk": f"WORKOUT_PLAN#{plan_id}",
        "plan_id": plan_id,
        "name": body.name,
        "week_start": body.week_start,
        "days": [{"day_of_week": d.day_of_week, "exercises": [e.model_dump() for e in d.exercises]} for d in body.days],
    }
    put_item(item)
    return item


@router.get("/plans")
def list_workout_plans(user_id: str = Depends(get_current_user)):
    return query_items(user_id, "WORKOUT_PLAN#")


@router.get("/plans/{plan_id}")
def get_workout_plan(plan_id: str, user_id: str = Depends(get_current_user)):
    item = get_item(user_id, f"WORKOUT_PLAN#{plan_id}")
    if not item:
        raise HTTPException(status_code=404, detail="workout plan not found")
    return item


@router.put("/plans/{plan_id}")
def update_workout_plan(
    plan_id: str,
    body: WorkoutPlanUpdate,
    user_id: str = Depends(get_current_user),
):
    item = get_item(user_id, f"WORKOUT_PLAN#{plan_id}")
    if not item:
        raise HTTPException(status_code=404, detail="workout plan not found")

    if body.name is not None:
        item["name"] = body.name
    if body.week_start is not None:
        item["week_start"] = body.week_start
    if body.days is not None:
        item["days"] = [{"day_of_week": d.day_of_week, "exercises": [e.model_dump() for e in d.exercises]} for d in body.days]

    put_item(item)
    return item


@router.delete("/plans/{plan_id}")
def delete_workout_plan(plan_id: str, user_id: str = Depends(get_current_user)):
    delete_item(user_id, f"WORKOUT_PLAN#{plan_id}")
    return {"deleted": plan_id}


@router.get("/streak")
def workout_streak(user_id: str = Depends(get_current_user)):
    workout_items = query_items(user_id, "WORKOUT#")
    workout_dates = sorted(
        {
            parsed
            for item in workout_items
            if item.get("date")
            for parsed in [_parse_workout_date(item["date"])]
            if parsed is not None
        }
    )

    if not workout_dates:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "total_workout_days": 0,
            "last_workout_date": None,
        }

    workout_set = set(workout_dates)
    today = date.today()
    current_anchor = today if today in workout_set else today - timedelta(days=1)
    current_streak = 0
    cursor = current_anchor
    while cursor in workout_set:
        current_streak += 1
        cursor -= timedelta(days=1)

    longest_streak = 1
    running = 1
    for i in range(1, len(workout_dates)):
        if workout_dates[i] == workout_dates[i - 1] + timedelta(days=1):
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 1

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_workout_days": len(workout_dates),
        "last_workout_date": workout_dates[-1].isoformat(),
    }


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
