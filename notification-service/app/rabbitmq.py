import json

import aio_pika
from aio_pika.abc import (
    AbstractConnection,
    AbstractIncomingMessage,
    AbstractRobustConnection,
)

from .config import settings
from .database import SessionLocal
from .models import Notification


async def connect_rabbitmq() -> AbstractRobustConnection:
    return await aio_pika.connect_robust(settings.rabbitmq_url)


async def handle_payment_events(message: AbstractIncomingMessage):
    async with message.process():
        event = json.loads(message.body.decode("utf-8"))

        notification = Notification(
            event_id=event["event_id"],
            event_type=event.get("status", "payment.succeeded"),
            order_id=event["order_id"],
            payment_id=event["payment_id"],
            amount=event["amount"],
            message=(
                f"Payment {event['payment_id']} for order "
                f"{event['order_id']} succeeded ({event['amount']})."
            ),
            event_created_at=event["created_at"],
        )

        with SessionLocal() as session:
            session.add(notification)
            session.commit()


async def start_payments_consume(connection: AbstractConnection):
    channel = await connection.channel()
    payment_exchange = await channel.declare_exchange(settings.payment_exchange_name)
    notification_queue = await channel.declare_queue(settings.notification_queue_name)

    await notification_queue.bind(
        payment_exchange,
        routing_key=settings.payment_succeeded_routing_key,
    )
    await notification_queue.consume(handle_payment_events)
