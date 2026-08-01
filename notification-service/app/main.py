from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.database import engine
from app.models import Base
from app.schemas import NotificationCreateSchema, NotificationReadSchema
from app.service import NotificationService
from app.config import NotFoundError
from app.dependencies import get_notification_service
from app.rabbitmq import connect_rabbitmq, start_payments_consume


@asynccontextmanager
async def lifespan(_: FastAPI):
    from app.models import Notification

    Base.metadata.create_all(bind=engine)

    connection = await connect_rabbitmq()
    await start_payments_consume(connection)

    try:
        yield
    finally:
        await connection.close()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(NotFoundError)
async def not_found_handler(_: Request, __: NotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Notification not found"},
    )


@app.get("/notifications", response_model=list[NotificationReadSchema])
def get_notifications(
    notification_service: NotificationService = Depends(get_notification_service),
):
    return notification_service.get_all()


@app.get("/notifications/{notification_id}", response_model=NotificationReadSchema)
def get_notification(
    notification_id: str,
    notification_service: NotificationService = Depends(get_notification_service),
):
    return notification_service.get(notification_id)


@app.post(
    "/notifications",
    response_model=NotificationReadSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_notification(
    payload: NotificationCreateSchema,
    notification_service: NotificationService = Depends(get_notification_service),
):
    return notification_service.create(payload)
