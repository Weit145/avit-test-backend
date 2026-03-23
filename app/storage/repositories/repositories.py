from sqlalchemy import select, exists, func
import uuid
from datetime import datetime
from typing import List
from ..postgres.db_hellper import db_helper
from ..models import Room, Schedule, Slot, Booking


# TODO GET(ID) flush
class SQLAlchemyAuthRepository:
    async def create_room(self, room:Room)->Room:
        async with db_helper.transaction() as session:
            session.add(room)
            await session.flush()
            await session.refresh(room)
            return room
    
    async def read_rooms(self)->List[Room]:
        async with db_helper.session_factory() as session:
            stmt = select(Room)
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def read_room(self, roomId: uuid.UUID)->Room|None:
        async with db_helper.session_factory() as session:
            stmt = select(Room).where(Room.id==roomId)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def read_schedule(self, roomId: uuid.UUID)->Schedule|None:
        async with db_helper.session_factory() as session:
            stmt = select(Schedule).where(Schedule.room_id==roomId)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def create_schedule(self, schedule:Schedule)->Schedule:
        async with db_helper.transaction() as session:
            session.add(schedule)
            await session.flush()
            await session.refresh(schedule)
            return schedule
    
    async def check_slots(self,roomId:uuid.UUID, start_of_day:datetime, end_of_day:datetime):
        async with db_helper.session_factory() as session:
            stmt = select(exists().where(
                Slot.room_id == roomId,
                Slot.start >= start_of_day,
                Slot.start < end_of_day
            ))
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def read_slots_without_booking(self, roomId:uuid.UUID, start_of_day:datetime, end_of_day:datetime)->List[Slot]:
        async with db_helper.session_factory() as session:
            stmt = select(Slot).where(Slot.room_id==roomId).where(Slot.start >= start_of_day, Slot.start < end_of_day).where(~Slot.bookings.any(Booking.status == "active"))
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def create_slots(self,slots:List[Slot])->List[Slot]:
        async with db_helper.transaction() as session:
            session.add_all(slots)
            await session.flush()
            return slots
    
    async def read_slot(self, id: uuid.UUID)->Slot|None:
        async with db_helper.session_factory() as session:
            stmt = select(Slot).where(Slot.id==id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def read_booking(self,slot_id:uuid.UUID)->Booking|None:
        async with db_helper.session_factory() as session:
            stmt = select(Booking).where( Booking.slot_id == slot_id ,Booking.status == "active")
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def create_booking(self,booking:Booking)->Booking:
        async with db_helper.transaction() as session:
            session.add(booking)
            await session.flush()
            await session.refresh(booking)
            return booking
    
    async def count_bookings(self)->int|None:
        async with db_helper.session_factory() as session:
            stmt = select(func.count()).select_from(Booking)
            result = await session.execute(stmt)
            return result.scalar()

    async def read_bookings(self, offset:int, page_size:int)->List[Booking]:
        async with db_helper.session_factory() as session:
            stmt = select(Booking).offset(offset).limit(page_size).order_by(Booking.created_at.desc())
            result = await session.execute(stmt)
            return list(result.scalars().all())