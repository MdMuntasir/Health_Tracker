from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.ai_service import generate_workout_plan, generate_diet_plan, generate_weekly_insights, chat
from app.utils.summary import get_weekly_summary
from app.utils.jwt import get_current_user

router = APIRouter()

class WorkoutPlanRequest(BaseModel):
    goal: str
    fitness_level: str
    recent_activity: str

class DietPlanRequest(BaseModel):
    calorie_goal: int
    protein_g: int
    carbs_g: int
    fat_g: int

class InsightsRequest(BaseModel):
    week_start_date: str

class ChatRequest(BaseModel):
    message: str

@router.post("/workout")
def ai_workout(body: WorkoutPlanRequest, user_id: str = Depends(get_current_user)):
    result = generate_workout_plan(body.goal, body.fitness_level, body.recent_activity)
    return {"result": result}

@router.post("/diet")
def ai_diet(body: DietPlanRequest, user_id: str = Depends(get_current_user)):
    result = generate_diet_plan(body.calorie_goal, body.protein_g, body.carbs_g, body.fat_g)
    return {"result": result}

@router.post("/insights")
def ai_insights(body: InsightsRequest, user_id: str = Depends(get_current_user)):
    summary = get_weekly_summary(user_id, body.week_start_date)
    summary["workouts_completed"] = summary.pop("total_workouts")
    result = generate_weekly_insights(summary)
    return {"result": result}

@router.post("/chat")
def ai_chat(body: ChatRequest, user_id: str = Depends(get_current_user)):
    result = chat(body.message)
    return {"result": result}
