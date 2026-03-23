from click import Option
from fastapi import APIRouter, status, Depends, Body, Path, Query
import uuid
from typing import Annotated, List
from app.service.service import service
from app.schemas.schemas_auth import Auth
from app.schemas.rooms import CreateRoom, OutRoom
from app.schemas.schedule import CreateSchedule, OutSchedule
from app.schemas.bookings import CreateBooking, OutBooking
from .dependes import check_admin_role, check_user_role, get_current_user


router = APIRouter(prefix="/bookings",tags=["Bookings"])

@router.post("/create/", status_code=status.HTTP_201_CREATED)
async def create_booking(
    user : Annotated[Auth, Depends(check_user_role)],
    booking : CreateBooking,
)->OutBooking:
    return  await service.create_booking(user,booking)


@router.get("/list/", status_code=status.HTTP_200_OK)
async def read_bookings(
    _ : Annotated[Auth, Depends(check_admin_role)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
)->List[OutBooking]:
    return  await service.read_bookings(page,page_size)
