from app.api.schemas import CreateBooking, OutBooking
from app.storage.models import Booking
import uuid
from typing import List


def to_bd(
    booking: CreateBooking, user_id: uuid.UUID, link: str | None = None
) -> Booking:
    return Booking(
        slot_id=booking.slotId, conference_link=link, user_id=user_id, status="active"
    )


def to_out(booking: Booking) -> OutBooking:
    return OutBooking(
        slotId=booking.slot_id,
        conferenceLink=booking.conference_link,
        id=booking.id,
        userId=booking.user_id,
        status=booking.status,
        createdAt=booking.created_at,
    )


def list_to_out(list_bd: List[Booking]) -> List[OutBooking]:
    return [to_out(x) for x in list_bd]
