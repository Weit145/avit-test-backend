import uuid
from sqlalchemy import Uuid, ForeignKey, DateTime, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from .base import Base

class Booking(Base):
    __tablename__ = "booking"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    slot_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("slot.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id:Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        default=uuid.uuid4
    )
    status: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="active"
    )
    conference_link: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    slot: Mapped["Slot"] = relationship(back_populates="bookings")

    __table_args__ = (
        Index("idx_booking_slot_status", "slot_id", "status"),
    )