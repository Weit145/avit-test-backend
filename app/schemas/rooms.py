import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from annotated_types import MaxLen, MinLen
from typing import Optional, Annotated


class Room(BaseModel):
    pass

class CreateRoom(Room):
    name: Annotated[str, MinLen(4), MaxLen(32)]
    description:Optional[str] = Field(default=None)
    capacity:Optional[int] = Field(default=None, gt=0)
    pass

class OutRoom(Room):
    id: uuid.UUID
    name: Annotated[str, MinLen(4), MaxLen(32)]
    description:Optional[str] = Field(default=None)
    capacity:Optional[int] = Field(default=None, gt=0)
    created_at: datetime
    pass