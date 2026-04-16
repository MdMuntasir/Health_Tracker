import uuid
from fastapi import APIRouter, HTTPException, Depends
import bcrypt
from app.models.user import UserRegister, UserLogin, UserProfileUpdate
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
    if body.height_cm is not None:
        user["height_cm"] = str(body.height_cm)
    put_item(user)
    token = create_token(user_id)
    response_user = {"user_id": user_id, "email": body.email, "name": body.name}
    if body.height_cm is not None:
        response_user["height_cm"] = str(body.height_cm)
    return {"access_token": token, "user": response_user}

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


@router.put("/profile")
def update_profile(body: UserProfileUpdate, user_id: str = Depends(get_current_user)):
    user = get_item(user_id, "PROFILE")
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    if body.name is not None:
        user["name"] = body.name
    if body.avatar_url is not None:
        user["avatar_url"] = body.avatar_url
    if body.height_cm is not None:
        user["height_cm"] = str(body.height_cm)

    put_item(user)
    return {k: v for k, v in user.items() if k not in ("password", "sk")}
