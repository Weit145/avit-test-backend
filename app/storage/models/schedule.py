import uuid
from sqlalchemy import Uuid
from sqlalchemy import Uuid, ForeignKey, ARRAY, Integer, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime
from .base import Base

class Schedule(Base):
    __tablename__ = "schedule"

    room_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True),ForeignKey("room.id", ondelete="CASCADE"),nullable=False)
    days_of_week: Mapped[list[int]] = mapped_column(ARRAY(Integer),nullable=False)
    start_time: Mapped[datetime.time] = mapped_column(nullable=False)
    end_time: Mapped[datetime.time] = mapped_column(nullable=False)

    __table_args__ = (UniqueConstraint("room_id", name="uq_schedule"),)
    
    room: Mapped["Room"] = relationship(back_populates="schedule")