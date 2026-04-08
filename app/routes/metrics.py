import uuid
from fastapi import APIRouter, HTTPException, Depends
from app.models.metrics import MetricCreate
from app.services.db_service import put_item, query_items
from app.utils.jwt import get_current_user

router = APIRouter()

@router.post("")
def log_metric(body: MetricCreate, user_id: str = Depends(get_current_user)):
    metric_id = str(uuid.uuid4())
    item = {
        "user_id": user_id,
        "sk": f"METRIC#{metric_id}",
        "metric_id": metric_id,
        "date": body.date,
    }
    if body.weight_kg is not None:
        item["weight_kg"] = str(body.weight_kg)
    if body.bmi is not None:
        item["bmi"] = str(body.bmi)
    if body.sleep_hours is not None:
        item["sleep_hours"] = str(body.sleep_hours)
    if body.steps is not None:
        item["steps"] = str(body.steps)
    put_item(item)
    return item

@router.get("")
def list_metrics(user_id: str = Depends(get_current_user)):
    return query_items(user_id, "METRIC#")

@router.get("/latest")
def latest_metric(user_id: str = Depends(get_current_user)):
    items = query_items(user_id, "METRIC#")
    if not items:
        raise HTTPException(status_code=404, detail="no metrics found")
    return sorted(items, key=lambda x: x.get("date", ""), reverse=True)[0]
