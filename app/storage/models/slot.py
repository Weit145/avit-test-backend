import uuid
from sqlalchemy import Uuid, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .base import Base


class Slot(Base):
    __tablename__ = "slot"

    room_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("room.id", ondelete="CASCADE"), nullable=False
    )
    start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    room: Mapped["Room"] = relationship(back_populates="slots")
    booking: Mapped["Booking"] = relationship(
        back_populates="slot", cascade="all, delete-orphan", uselist=False
    )

    __table_args__ = (
        UniqueConstraint("room_id", "start", "end"),
        Index("idx_slot_room_time", "room_id", "start", "end"),
    )
