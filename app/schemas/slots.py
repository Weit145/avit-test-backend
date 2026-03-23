import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from annotated_types import MaxLen, MinLen
from typing import Optional, Annotated


class Slot(BaseModel):
    pass

# class CreateRoom(Room):
#     pass

class OutSlot(Slot):
    id: uuid.UUID
    roomId: uuid.UUID
    start: datetime
    end: datetime
    pass