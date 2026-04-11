import time
import hashlib
from google import genai
from google.genai.errors import ClientError
from app.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

_MODEL_CHAIN = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
]

_cache: dict = {}
_CACHE_TTL = 3600


def _cache_get(prompt: str):
    key = hashlib.md5(prompt.encode()).hexdigest()
    entry = _cache.get(key)
    if entry and (time.time() - entry[0]) < _CACHE_TTL:
        return entry[1]
    return None


def _cache_set(prompt: str, text: str):
    key = hashlib.md5(prompt.encode()).hexdigest()
    _cache[key] = (time.time(), text)


def _parse_retry_delay(error: ClientError) -> float:
    try:
        details = error.args[0] if error.args else {}
        if isinstance(details, dict):
            for detail in details.get("error", {}).get("details", []):
                delay = detail.get("retryDelay", "")
                if delay:
                    return float(delay.rstrip("s"))
    except Exception:
        pass
    return 30.0


def _generate(prompt: str) -> str:
    cached = _cache_get(prompt)
    if cached:
        return cached

    last_error = None
    for model in _MODEL_CHAIN:
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            _cache_set(prompt, response.text)
            return response.text
        except ClientError as e:
            if e.code == 429:
                last_error = e
                delay = min(_parse_retry_delay(e), 8.0)
                time.sleep(delay)
                try:
                    response = client.models.generate_content(model=model, contents=prompt)
                    _cache_set(prompt, response.text)
                    return response.text
                except ClientError:
                    continue
            raise

    raise last_error


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
