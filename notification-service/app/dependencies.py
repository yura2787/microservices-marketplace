from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.service import NotificationService


def get_notification_service(
    db: Session = Depends(get_db),
) -> NotificationService:
    return NotificationService(db)
