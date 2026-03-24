from app.api.schemas import CreateRoom, OutRoom
from app.storage.models import Room
from typing import List


def to_bd(room: CreateRoom) -> Room:
    return Room(name=room.name, description=room.description, capacity=room.capacity)


def to_out(room: Room) -> OutRoom:
    return OutRoom(
        id=room.id,
        name=room.name,
        description=room.description,
        capacity=room.capacity,
        created_at=room.created_at,
    )


def list_to_out(rooms: List[Room]) -> List[OutRoom]:
    return [to_out(x) for x in rooms]
