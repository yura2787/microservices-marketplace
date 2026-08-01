from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    event_type: str
    order_id: str
    payment_id: str
    amount: int
    message: str
    event_created_at: str


class NotificationReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_id: str
    event_type: str
    order_id: str
    payment_id: str
    amount: int
    message: str
    event_created_at: str
    received_at: datetime
