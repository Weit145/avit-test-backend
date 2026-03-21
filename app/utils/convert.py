from app.schemas.rooms import CreateRoom, OutRoom
from app.storage.models.room import Room

def convert_create_room_to_bd(room: CreateRoom)->Room:
    return Room(
        name = room.name,
        description = room.description,
        capacity = room.capacity
    )

def convert_room_bd_to_out(room: Room)-> OutRoom:
    return OutRoom(
        id = room.id,
        name = room.name,
        description = room.description,
        capacity = room.capacity,
        created_at =  room.created_at,
    )