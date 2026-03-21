from fastapi import APIRouter, status, Depends, Body
from typing import Annotated
from app.service.service import service
from app.schemas.schemas_auth import Auth
from app.schemas.rooms import CreateRoom, OutRoom
from .dependes import check_admin_role, check_user_role


router = APIRouter(prefix="/rooms",tags=["Rooms"])



@router.post("/create/", status_code=status.HTTP_201_CREATED)
async def create_room(
    _ : Annotated[Auth, Depends(check_admin_role)],
    room: CreateRoom = Body(...),
)->OutRoom:
    return  await service.create_room(room)