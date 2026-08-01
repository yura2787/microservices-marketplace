from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = (
        "postgresql+psycopg2://notifications:notifications@localhost:5435/notifications"
    )
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672"
    payment_succeeded_routing_key: str = "payment.succeeded"
    payment_exchange_name: str = "payment.events"
    notification_queue_name: str = "notification.results"


settings = Settings()


class NotFoundError(Exception):
    pass
