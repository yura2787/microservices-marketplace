from contextlib import asynccontextmanager

from aiokafka import AIOKafkaProducer
from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.database import engine
from app.models import Base
from app.config import NotFoundError, settings
from app.schemas import OrderCreateSchema, OrderReadSchema
from app.service import OrderService
from app.dependencies import get_order_service
from app.rabbitmq import connect_rabbitmq, start_payments_consume
from app.kafka import create_kafka_producer, publish_kafka_event
from app.events import build_order_created_event


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    connection = await connect_rabbitmq()
    await start_payments_consume(connection)

    kafka_producer: AIOKafkaProducer = create_kafka_producer()
    await kafka_producer.start()
    app.state.kafka_producer = kafka_producer

    try:
        yield
    finally:
        await kafka_producer.stop()
        await connection.close()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(NotFoundError)
async def not_found_handler(_: Request, __: NotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Order not found"},
    )


@app.get("/orders/{order_id}", response_model=OrderReadSchema)
def get_order(
    order_id,
    order_service: OrderService = Depends(get_order_service)
):
    return order_service.get(order_id)


@app.get("/orders", response_model=list[OrderReadSchema])
def get_orders(
    order_service: OrderService = Depends(get_order_service)
):
    return order_service.get_all()


@app.post("/orders", response_model=OrderReadSchema)
async def create_order(
    request: Request,
    payload: OrderCreateSchema,
    order_service: OrderService = Depends(get_order_service)
):
    order = order_service.create(payload)

    event = build_order_created_event(order)
    await publish_kafka_event(
        request.app.state.kafka_producer,
        settings.kafka_order_topic,
        event,
    )

    return order
