from fastapi import HTTPException, status
import logging
import asyncio
import uuid
from typing import List
from datetime import UTC, datetime, timedelta,timezone, date
from app.core.config import settings
from app.schemas.schemas_auth import JWT
from app.schemas.schemas_auth import Auth
from app.schemas.rooms import CreateRoom, OutRoom
from app.schemas.schedule import CreateSchedule , OutSchedule
from app.schemas.bookings import CreateBooking, OutBooking
from app.schemas.slots import OutSlot
from app.storage.models import Schedule
from app.storage.repositories.repositories import SQLAlchemyAuthRepository
from app.utils.convert import (
    convert_create_room_to_bd, 
    convert_room_bd_to_out, 
    convert_list_bd_to_out, 
    convert_create_schedule_to_bd,
    convert_schedule_bd_to_out,
    cunvert_slot_db,
    convert_slot_out,
    convert_booking_bd,
    convert_booking_out,
    convert_list_booking_out
)

import jwt

logger = logging.getLogger(__name__)


# TODO REDACT SESSION
class Service:
    def __init__(self):
        self.repo = SQLAlchemyAuthRepository()
        pass
    
    def create_token(self,role:str)->JWT:
        expire = datetime.now(UTC) + timedelta(minutes=settings.time_jwt_minutes)
        to_encode = {
            "user_id": settings.admin_id if role == "admin" else settings.user_id,
            "role": role,
            "exp": expire,
        }
        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        return JWT(jwt=encoded_jwt)
    
    async def create_room(self,room:CreateRoom)->OutRoom:
        room_bd = convert_create_room_to_bd(room)
        result = await self.repo.create_room(room_bd)
        return convert_room_bd_to_out(result)

    async def read_rooms(self)->List[OutRoom]:
        result = await self.repo.read_rooms()
        return convert_list_bd_to_out(result)
    
    async def create_schedule(
        self,
        roomId:uuid.UUID, 
        schedule: CreateSchedule
    )->OutSchedule:
        room_task = asyncio.create_task(self.repo.read_room(roomId))
        schedule_task = asyncio.create_task(self.repo.read_schedule(roomId))
        room, existing_schedule = await asyncio.gather(room_task, schedule_task)
        if room is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found",
            )
        if existing_schedule is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Schedule already create",
            )
        schedule_bd = convert_create_schedule_to_bd(schedule,roomId)
        result = await self.repo.create_schedule(schedule_bd)
        return convert_schedule_bd_to_out(result)

    async def read_slots(self, roomId:uuid.UUID,date:date)->List[OutSlot]:
        schedule= await self.repo.read_schedule(roomId)
        logger.info(date.isoweekday())
        logger.info(schedule.days_of_week)
        if schedule is None or date.isoweekday() not in schedule.days_of_week:
            return []
        start_of_day = datetime.combine(date, schedule.start_time, tzinfo=timezone.utc)
        end_of_day = datetime.combine(date, schedule.end_time, tzinfo=timezone.utc)
        check = await self.repo.check_slots(roomId,start_of_day,end_of_day)
        logger.info(check)
        if check is None or not check:
            list_slot = []
            current = start_of_day
            step = timedelta(minutes=30)
            while current + step <= end_of_day:
                list_slot.append(cunvert_slot_db(roomId, current, current + step))
                current += step
            slots_created = await self.repo.create_slots(list_slot) 
            return convert_slot_out(slots_created)

        result = await self.repo.read_slots_without_booking(roomId,start_of_day,end_of_day)
        return convert_slot_out(result)
    
    
    async def create_booking(self,user:Auth,booking: CreateBooking)->OutBooking:
        
        slot = await self.repo.read_slot(booking.slotId)
        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slot not found",
            )
        if slot.start < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slot is in the past",
            )
        check_brooked = await self.repo.read_booking(booking.slotId)
        if check_brooked:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Slot already booked",
            )
        link = None
        if booking.createConferenceLink:
            link = "https://kload.ru/"
        booking_bd = convert_booking_bd(booking,user.uuid ,link)
        booking_bd.status = "active"
        result = await self.repo.create_booking(booking_bd)
        return convert_booking_out(result)
    
    async def read_bookings(self,page:int, page_size:int)->List[OutBooking]:
        total = await self.repo.count_bookings()
        if total is None:
            return []
        offset = (page-1)*page_size
        result = await self.repo.read_bookings(offset, page_size)
        return convert_list_booking_out(result)
service = Service()