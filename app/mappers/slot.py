from app.api.schemas import OutSlot
from app.storage.models import Slot
from datetime import datetime
import uuid
from typing import List


def to_bd(roomId: uuid.UUID, start_of_day: datetime, end_of_day: datetime) -> Slot:
    return Slot(room_id=roomId, start=start_of_day, end=end_of_day)


def list_to_out(slots: List[Slot]) -> List[OutSlot]:
    list_out = []
    for i in slots:
        list_out.append(
            OutSlot(
                id=i.id,
                roomId=i.room_id,
                start=i.start,
                end=i.end,
            )
        )
    return list_out
