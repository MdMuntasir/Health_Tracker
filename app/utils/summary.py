from datetime import datetime, timedelta
from app.services.db_service import query_items

def get_summary_for_range(user_id, start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    dates = {
        (start + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range((end - start).days + 1)
    }

    nutrition = [n for n in query_items(user_id, "NUTRITION#") if n.get("date") in dates]
    workouts = [w for w in query_items(user_id, "WORKOUT#") if w.get("date") in dates]
    metrics = [m for m in query_items(user_id, "METRIC#") if m.get("date") in dates]

    avg_calories = (sum(float(n.get("calories", 0)) for n in nutrition) / len(nutrition)) if nutrition else 0
    avg_sleep = (sum(float(m.get("sleep_hours", 0)) for m in metrics) / len(metrics)) if metrics else 0
    avg_steps = (sum(float(m.get("steps", 0)) for m in metrics) / len(metrics)) if metrics else 0
    avg_weight = (sum(float(m.get("weight_kg", 0)) for m in metrics) / len(metrics)) if metrics else 0

    return {
        "avg_calories": avg_calories,
        "workouts_completed": len(workouts),
        "total_workouts": len(workouts),
        "avg_sleep": avg_sleep,
        "avg_steps": avg_steps,
        "avg_weight": avg_weight,
    }


def get_weekly_summary(user_id, week_start):
    start = datetime.strptime(week_start, "%Y-%m-%d").date()
    end = start + timedelta(days=6)
    return get_summary_for_range(user_id, start.isoformat(), end.isoformat())
