from pydantic import BaseModel,Field
import uuid
import datetime
from typing import Any, Optional

class Booking(BaseModel):
    slotId : uuid.UUID
    createConferenceLink : Any


class CreateBooking(Booking):
    createConferenceLink : Optional[bool] = Field(default=False)

class OutBooking(Booking):
    id: uuid.UUID
    userId: uuid.UUID
    status: str
    createConferenceLink: Optional[str] = None
    createdAt:datetime.datetime