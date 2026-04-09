from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.routes import auth, workout, nutrition, metrics, goals, ai
import uvicorn

app = FastAPI(title="Health Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(workout.router, prefix="/workouts", tags=["workouts"])
app.include_router(nutrition.router, prefix="/nutrition", tags=["nutrition"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
app.include_router(goals.router, prefix="/goals", tags=["goals"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])

@app.get("/")
def root():
    return {"status": "ok", "message": "Health Tracker API"}

# handler = Mangum(app)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
