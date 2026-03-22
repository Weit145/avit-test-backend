from fastapi import APIRouter, status, Depends, Body, Path
import uuid
from typing import Annotated, List
from app.service.service import service
from app.schemas.schemas_auth import Auth
from app.schemas.rooms import CreateRoom, OutRoom
from app.schemas.schedule import CreateSchedule, OutSchedule
from .dependes import check_admin_role, check_user_role, get_current_user


router = APIRouter(prefix="/rooms",tags=["Rooms"])

@router.get("/list/", status_code=status.HTTP_201_CREATED)
async def create_room(
    _ : Annotated[Auth, Depends(get_current_user)],
)->List[OutRoom]:
    return  await service.read_rooms()


@router.post("/create/", status_code=status.HTTP_201_CREATED)
async def create_room(
    _ : Annotated[Auth, Depends(check_admin_role)],
    room: CreateRoom = Body(...),
)->OutRoom:
    return  await service.create_room(room)

@router.post("/{roomId}/schedule/create/", status_code=status.HTTP_201_CREATED)
async def create_room(
    _ : Annotated[Auth, Depends(check_admin_role)],
    roomId: Annotated[uuid.UUID, Path(title="The ID of the rooms to create schedule")],
    schedule: CreateSchedule = Body(...), 
)->OutSchedule:
    return  await service.create_schedule(roomId,schedule)
