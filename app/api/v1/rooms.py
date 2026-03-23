from fastapi import APIRouter, status, Depends, Body, Path, Query
import uuid
from datetime import date
from typing import Annotated, List
from app.service.service import service
from app.schemas import Auth, CreateRoom, OutRoom, CreateSchedule, OutSchedule, OutSlot
from .dependencies import check_admin_role, get_current_user


router = APIRouter(prefix="/rooms",tags=["Rooms"])

@router.get("/list/", status_code=status.HTTP_200_OK, response_model=List[OutRoom])
async def read_rooms(
    _ : Annotated[Auth, Depends(get_current_user)],
)->List[OutRoom]:
    return  await service.read_rooms()


@router.post("/create/", status_code=status.HTTP_201_CREATED, response_model=OutRoom)
async def create_room(  
    _ : Annotated[Auth, Depends(check_admin_role)],
    room:  Annotated[CreateRoom, Body(...)]
)->OutRoom:
    return  await service.create_room(room)


@router.post("/{roomId}/schedule/create/", status_code=status.HTTP_201_CREATED, response_model=OutSchedule)
async def create_schedule(
    _ : Annotated[Auth, Depends(check_admin_role)],
    roomId: Annotated[uuid.UUID, Path(title="The ID of the rooms to create schedule")],
    schedule:  Annotated[CreateSchedule, Body(...)], 
)->OutSchedule:
    return  await service.create_schedule(roomId,schedule)


@router.get("/{roomId}/slots/list", status_code=status.HTTP_200_OK, response_model=List[OutSlot])
async def read_slots(
    _ : Annotated[Auth, Depends(get_current_user)],
    roomId: Annotated[uuid.UUID, Path(title="The ID of the rooms to check slots")],
    date: Annotated[date, Query(description="Date in YYYY-MM-DD format")]
)->List[OutSlot]:
    return await service.read_slots(roomId,date)