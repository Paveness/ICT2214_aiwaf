from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.user_model import authenticate_user

router = APIRouter()

@router.post("/example")
def example():
 
    return {
        "status": "ok",
        "user": user
    }
