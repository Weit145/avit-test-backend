from fastapi import APIRouter, status, Depends, Path, Query
import uuid
from typing import Annotated, List
from app.service.service import service
from app.api.schemas import CreateBooking, OutBooking, Auth
from .dependencies import check_admin_role, check_user_role


router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/create/", status_code=status.HTTP_201_CREATED, response_model=OutBooking)
async def create_booking(
    user: Annotated[Auth, Depends(check_user_role)],
    booking: CreateBooking,
) -> OutBooking:
    return await service.create_booking(user, booking)


@router.get("/list/", status_code=status.HTTP_200_OK, response_model=List[OutBooking])
async def list_bookings(
    _: Annotated[Auth, Depends(check_admin_role)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> List[OutBooking]:
    return await service.list_bookings(page, page_size)


@router.get("/my/", status_code=status.HTTP_200_OK, response_model=List[OutBooking])
async def read_my_bookings(
    user: Annotated[Auth, Depends(check_user_role)],
) -> List[OutBooking]:
    return await service.read_my_bookings(user)


@router.post("{bookingId}/cancel", status_code=status.HTTP_200_OK)
async def cancel_booking(
    user: Annotated[Auth, Depends(check_user_role)],
    bookingId: Annotated[uuid.UUID, Path(title="The ID of the booking to cancel")],
) -> None:
    return await service.cancel_booking(user, bookingId)
