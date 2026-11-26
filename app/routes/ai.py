from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from app.services.ai_service import generate_workout_plan, generate_diet_plan, generate_weekly_insights
from app.services.chat_service import (
    DEFAULT_CONVERSATION_ID,
    MAX_HISTORY_MESSAGES,
    clear_conversation,
    get_conversation,
    handle_chat,
)
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
    conversation_id: str = Field(
        default=DEFAULT_CONVERSATION_ID,
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$",
    )

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
    result = handle_chat(user_id, body.message, body.conversation_id)
    return {
        "result": result["reply"],
        "conversation_id": result["conversation_id"],
        "summary": result["summary"],
        "message_count": result["message_count"],
        "updated_at": result["updated_at"],
    }

@router.get("/chat")
def ai_chat_history(
    conversation_id: str = Query(
        default=DEFAULT_CONVERSATION_ID,
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$",
    ),
    limit: int = Query(default=MAX_HISTORY_MESSAGES, ge=1, le=500),
    user_id: str = Depends(get_current_user),
):
    return get_conversation(user_id, conversation_id, limit)

@router.delete("/chat")
def ai_chat_clear(
    conversation_id: str = Query(
        default=DEFAULT_CONVERSATION_ID,
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$",
    ),
    user_id: str = Depends(get_current_user),
):
    return clear_conversation(user_id, conversation_id)
