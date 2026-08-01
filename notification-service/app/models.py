from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for ORM models."""

    id: Mapped[str] = mapped_column(
        primary_key=True,
        default=lambda: str(uuid4()),
    )


class Notification(Base):
    __tablename__ = "notifications"

    event_id: Mapped[str]
    event_type: Mapped[str]
    order_id: Mapped[str]
    payment_id: Mapped[str]
    amount: Mapped[int]
    message: Mapped[str]
    # When the source event was produced (from the event payload).
    event_created_at: Mapped[str]
    # When this notification row was stored by our consumer.
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
