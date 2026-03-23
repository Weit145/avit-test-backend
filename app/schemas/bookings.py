from pydantic import BaseModel,Field
import uuid
import datetime
from typing import Any, Optional

class Booking(BaseModel):
    pass


class CreateBooking(Booking):
    slotId : uuid.UUID
    conferenceLink : Optional[bool] = Field(default=False)

class OutBooking(Booking):
    id: uuid.UUID
    slotId : uuid.UUID
    userId: uuid.UUID
    status: str
    conferenceLink: Optional[str] = None
    createdAt:datetime.datetime