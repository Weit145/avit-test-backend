from fastapi import APIRouter, status, Body
from typing import Literal
from app.schemas.schemas_auth import JWT
from app.service.service import service

router = APIRouter(tags=["Auth"])



@router.post("/dummyLogin/", status_code=status.HTTP_200_OK)
async def dummy_login(
    role: Literal["admin", "user"] = Body(...)
)->JWT:
    return service.create_token(role)