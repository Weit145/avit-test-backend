from fastapi import APIRouter, status, Depends, Body, Path, Query
import uuid
from datetime import date
from typing import Annotated, List
from app.service.service import service
from app.api.schemas import (
    Auth,
    CreateRoom,
    OutRoom,
    CreateSchedule,
    OutSchedule,
    OutSlot,
)
from .dependencies import check_admin_role, get_current_user


router = APIRouter(prefix="/rooms", tags=["Rooms"])


# TODO написать редми что сделан ограничение
@router.get("/list/", status_code=status.HTTP_200_OK, response_model=List[OutRoom])
async def list_rooms(
    _: Annotated[Auth, Depends(get_current_user)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> List[OutRoom]:
    return await service.list_rooms(page, page_size)


@router.post("/create/", status_code=status.HTTP_201_CREATED, response_model=OutRoom)
async def create_room(
    _: Annotated[Auth, Depends(check_admin_role)],
    room: Annotated[CreateRoom, Body(...)],
) -> OutRoom:
    return await service.create_room(room)


@router.post(
    "/{roomId}/schedule/create/",
    status_code=status.HTTP_201_CREATED,
    response_model=OutSchedule,
)
async def create_schedule(
    _: Annotated[Auth, Depends(check_admin_role)],
    roomId: Annotated[uuid.UUID, Path(title="The ID of the rooms to create schedule")],
    schedule: Annotated[CreateSchedule, Body(...)],
) -> OutSchedule:
    return await service.create_schedule(roomId, schedule)


@router.get(
    "/{roomId}/slots/list", status_code=status.HTTP_200_OK, response_model=List[OutSlot]
)
async def list_slots(
    _: Annotated[Auth, Depends(get_current_user)],
    roomId: Annotated[uuid.UUID, Path(title="The ID of the rooms to check slots")],
    date: Annotated[date, Query(description="Date in YYYY-MM-DD format")],
) -> List[OutSlot]:
    return await service.list_slots(roomId, date)
