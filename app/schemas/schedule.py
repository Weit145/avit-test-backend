import uuid
from datetime import datetime, timedelta, time
from pydantic import BaseModel, Field, field_validator, model_validator
from annotated_types import MaxLen, MinLen
from typing import Optional, Annotated, List
import re


class Schedule(BaseModel):
    daysOfWeek: Annotated[List[int], MinLen(1), MaxLen(7)]
    startTime:time
    endTime:time
    
    @field_validator('daysOfWeek')
    def validate_days_of_week(cls, days):
        for day in days:
            if not 1 <= day <= 7:
                raise ValueError('Format Days error')
            if len(days) != len(set(days)):
                raise ValueError('No unique values')
        return days

    @model_validator(mode='after')
    def validate_time_range(self):
        today = datetime.today().date()
        start_dt = datetime.combine(today, self.startTime)
        end_dt = datetime.combine(today, self.endTime)
        if end_dt < start_dt:
            end_dt += timedelta(days=1)
        if (end_dt - start_dt) < timedelta(minutes=30):
            raise ValueError('Not 30 min')
        return self
    pass

class CreateSchedule(Schedule):
    pass

class OutSchedule(Schedule):
    id: uuid.UUID
    roomId: uuid.UUID
    pass