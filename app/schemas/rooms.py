import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from annotated_types import MaxLen, MinLen
from typing import Optional, Annotated


class Room(BaseModel):
    name: Annotated[str, MinLen(4), MaxLen(32)]
    description:Optional[str] = Field(default=None)
    capacity:Optional[int] = Field(default=None, gt=0)
    pass

class CreateRoom(Room):
    pass

class OutRoom(Room):
    id: uuid.UUID
    created_at: datetime
    pass