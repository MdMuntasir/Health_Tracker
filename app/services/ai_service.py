from google import genai
from app.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.0-flash"

def _generate(prompt):
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text

def generate_workout_plan(goal, fitness_level, recent_activity):
    prompt = f"Create a workout plan for someone with goal: {goal}, fitness level: {fitness_level}, recent activity: {recent_activity}."
    return _generate(prompt)

def generate_diet_plan(calorie_goal, protein_g, carbs_g, fat_g):
    prompt = f"Create a diet plan for: {calorie_goal} calories, {protein_g}g protein, {carbs_g}g carbs, {fat_g}g fat per day."
    return _generate(prompt)

def generate_weekly_insights(summary):
    prompt = (
        f"Give weekly health insights based on: "
        f"avg calories {summary.get('avg_calories')}, "
        f"workouts completed {summary.get('workouts_completed')}, "
        f"avg sleep {summary.get('avg_sleep')} hours, "
        f"avg steps {summary.get('avg_steps')}."
    )
    return _generate(prompt)

def chat(user_message):
    prompt = f"You are a health assistant. User says: {user_message}"
    return _generate(prompt)
