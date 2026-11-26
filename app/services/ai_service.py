import json
import re
import time
import hashlib
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from app.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

_MODEL_CHAIN = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
]

_cache: dict = {}
_CACHE_TTL = 3600

_CHAT_SYSTEM_PROMPT = (
    "You are a helpful, practical health and fitness assistant. Give safe, "
    "evidence-informed advice and stay consistent with what the user has already "
    "shared. If the user describes severe symptoms or a medical emergency, tell "
    "them to contact a healthcare professional."
)


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


def _generate(prompt: str, use_cache: bool = True, json_output: bool = False) -> str:
    if use_cache:
        cached = _cache_get(prompt)
        if cached:
            return cached

    config = (
        types.GenerateContentConfig(response_mime_type="application/json")
        if json_output
        else None
    )

    last_error = None
    for model in _MODEL_CHAIN:
        try:
            response = client.models.generate_content(
                model=model, contents=prompt, config=config
            )
            text = response.text or ""
            if use_cache:
                _cache_set(prompt, text)
            return text
        except ClientError as e:
            if e.code == 429:
                last_error = e
                delay = min(_parse_retry_delay(e), 8.0)
                time.sleep(delay)
                try:
                    response = client.models.generate_content(
                        model=model, contents=prompt, config=config
                    )
                    text = response.text or ""
                    if use_cache:
                        _cache_set(prompt, text)
                    return text
                except ClientError:
                    continue
            raise

    raise last_error


def _parse_json_object(raw: str):
    if not raw:
        return None

    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    candidates = [text]
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        candidates.append(match.group(0))

    for candidate in candidates:
        try:
            data = json.loads(candidate)
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(data, dict):
            return data

    return None


def _fallback_summary(previous_summary, user_message, assistant_message, limit=4000):
    """Heuristic summary used when the model does not return valid JSON."""
    parts = [
        part
        for part in (
            previous_summary,
            f"User: {user_message}\nAssistant: {assistant_message}",
        )
        if part
    ]
    return "\n\n".join(parts).strip()[-limit:]


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


def chat_with_summary(user_message, previous_summary=None):
    """Answer the user and return an updated rolling summary of the conversation.

    Both values come from a single model call so a chat turn stays within
    serverless request timeouts. The summary is persisted by the caller and is
    fed back in as ``previous_summary`` on the next turn.
    """
    prompt = "\n\n".join(
        [
            _CHAT_SYSTEM_PROMPT,
            "Conversation summary so far:\n"
            + (previous_summary.strip() if previous_summary else "(new conversation)"),
            f"New user message:\n{user_message}",
            (
                "Respond with a single JSON object containing exactly two keys:\n"
                '  "reply": your answer to the user (markdown is allowed),\n'
                '  "summary": an updated summary of the ENTIRE conversation so far, '
                "including this new exchange. Keep the user's goals, conditions, "
                "constraints, preferences, and key advice already given. Write it in "
                "third person and keep it under 300 words.\n"
                "Return only the JSON object, with no markdown fences or preamble."
            ),
        ]
    )

    raw = _generate(prompt, use_cache=False, json_output=True)
    data = _parse_json_object(raw)

    reply = data.get("reply") if data else None
    if isinstance(reply, str) and reply.strip():
        reply = reply.strip()
        summary = data.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            summary = _fallback_summary(previous_summary, user_message, reply)
        return reply, summary.strip()

    reply = (raw or "").strip() or "Sorry, I couldn't generate a response. Please try again."
    return reply, _fallback_summary(previous_summary, user_message, reply)
