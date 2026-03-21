from sqlalchemy import text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .base import Base


class Room(Base):
    __tablename__ = "room"

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str| None] = mapped_column(nullable=True ,default=None)
    capacity: Mapped[int| None] = mapped_column(nullable=True ,default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    schedule: Mapped["Schedule"] = relationship(back_populates="room", uselist=False)
    slots: Mapped[list["Slot"]] = relationship(back_populates="room", cascade="all, delete-orphan")