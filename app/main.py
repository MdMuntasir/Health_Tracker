from fastapi import FastAPI
from app.routes import auth
import uvicorn

app = FastAPI(title="Health Tracker API")

app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
def root():
    return {"status": "ok", "message": "Health Tracker API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
