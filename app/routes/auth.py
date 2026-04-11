import uuid
from fastapi import APIRouter, HTTPException, Depends
import bcrypt
from app.models.user import UserRegister, UserLogin
from app.services.db_service import put_item, get_item, get_user_by_email
from app.utils.jwt import create_token, get_current_user

router = APIRouter()

@router.post("/register")
def register(body: UserRegister):
    if get_user_by_email(body.email):
        raise HTTPException(status_code=400, detail="email already registered")
    user_id = str(uuid.uuid4())
    user = {
        "user_id": user_id,
        "sk": "PROFILE",
        "email": body.email,
        "name": body.name,
        "password": bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode(),
    }
    put_item(user)
    token = create_token(user_id)
    return {"access_token": token, "user": {"user_id": user_id, "email": body.email, "name": body.name}}

@router.post("/login")
def login(body: UserLogin):
    user = get_user_by_email(body.email)
    if not user or not bcrypt.checkpw(body.password.encode(), user["password"].encode()):
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = create_token(user["user_id"])
    return {"access_token": token, "user": {k: v for k, v in user.items() if k not in ("password", "sk")}}

@router.get("/me")
def me(user_id: str = Depends(get_current_user)):
    user = get_item(user_id, "PROFILE")
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return {k: v for k, v in user.items() if k not in ("password", "sk")}
