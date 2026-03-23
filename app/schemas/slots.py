import uuid
from datetime import datetime
from pydantic import BaseModel


class Slot(BaseModel):
    pass

class OutSlot(Slot):
    id: uuid.UUID
    roomId: uuid.UUID
    start: datetime
    end: datetime
    pass