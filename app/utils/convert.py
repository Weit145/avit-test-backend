from app.schemas.rooms import CreateRoom, OutRoom
from app.schemas.schedule import CreateSchedule, OutSchedule
from app.storage.models import Room, Schedule
import uuid
from typing import List

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

def convert_list_bd_to_out(rooms: List[Room])-> List[OutRoom]:
    return [convert_room_bd_to_out(x) for x in rooms]


def convert_create_schedule_to_bd(schedule: CreateSchedule, room_id: uuid.UUID)->Schedule:
    return Schedule(
        room_id = room_id,
        days_of_week = schedule.daysOfWeek,
        start_time = schedule.startTime,
        end_time = schedule.endTime
    )
    
def convert_schedule_bd_to_out(schedule: Schedule)-> OutRoom:
    return OutSchedule(
        id = schedule.id,
        roomId = schedule.room_id,
        daysOfWeek = schedule.days_of_week,
        startTime = schedule.start_time,
        endTime =  schedule.end_time,
    )