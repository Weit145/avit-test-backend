from app.api.v1 import slots
from app.schemas.rooms import CreateRoom, OutRoom
from app.schemas.schedule import CreateSchedule, OutSchedule
from app.schemas.slots import OutSlot
from app.schemas.bookings import CreateBooking, OutBooking
from app.storage.models import Room, Schedule, Slot, Booking
from datetime import datetime, timedelta
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
    
def convert_schedule_bd_to_out(schedule: Schedule)-> OutSchedule:
    return OutSchedule(
        id = schedule.id,
        roomId = schedule.room_id,
        daysOfWeek = schedule.days_of_week,
        startTime = schedule.start_time,
        endTime =  schedule.end_time,
    )

def cunvert_slot_db(roomId:uuid.UUID,start_of_day:datetime, end_of_day:datetime)->Slot:
    return Slot(
        room_id = roomId,
        start = start_of_day,
        end = end_of_day
    )

def convert_slot_out(slots:List[Slot])->List[OutSlot]:
    list_out =[]
    for i in slots:
        list_out.append(
            OutSlot(
                id = i.id,
                roomId = i.room_id,
                start= i.start,
                end= i.end,
            )
        )
    return list_out

def convert_booking_bd(booking:CreateBooking, user_id:uuid.UUID, link:str|None = None)->Booking:
    return Booking(
        slot_id = booking.slotId,
        conference_link = link,
        user_id = user_id,
    )

def convert_booking_out(booking:Booking)->OutBooking:
    return OutBooking(
        slotId=booking.slot_id,
        createConferenceLink=booking.conference_link,
        id = booking.id,
        userId = booking.user_id,
        status= booking.status,
        createdAt= booking.created_at
    )

def convert_list_booking_out(list_bd:List[Booking])->List[OutBooking]:
    return [convert_booking_out(x) for x in list_bd]