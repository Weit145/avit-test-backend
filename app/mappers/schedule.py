from app.api.schemas import CreateSchedule, OutSchedule
from app.storage.models import Schedule
import uuid


def to_bd(schedule: CreateSchedule, room_id: uuid.UUID) -> Schedule:
    return Schedule(
        room_id=room_id,
        days_of_week=schedule.daysOfWeek,
        start_time=schedule.startTime,
        end_time=schedule.endTime,
    )


def to_out(schedule: Schedule) -> OutSchedule:
    return OutSchedule(
        id=schedule.id,
        roomId=schedule.room_id,
        daysOfWeek=schedule.days_of_week,
        startTime=schedule.start_time,
        endTime=schedule.end_time,
    )
