from datetime import UTC, datetime
from uuid import uuid4

from .schemas import OrderReadSchema


def build_order_created_event(order: OrderReadSchema) -> dict:
    return {
        "event_id": str(uuid4()),
        "created_at": datetime.now(UTC).isoformat(),
        "order_id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "total_amount": order.total_amount,
        "event_type": "order.created",
    }
