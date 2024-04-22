import json
import logging

from django.conf import settings
from django.utils import timezone

from .config import create_producer

logger = logging.getLogger(__name__)


def log_event(err, msg):
    """
    https://docs.confluent.io/clients-confluent-kafka-python/current/overview.html#asynchronous-writes
    """
    if err is not None:
        logger.error(f"Failed to deliver message: {str(msg)} : {str(err)}")


def send_event(
    *, topic: str, action: str = "", key: any = None, value: dict = None
) -> bool:
    """
    Send event to Kafka
    https://docs.confluent.io/clients-confluent-kafka-python/current/overview.html#asynchronous-writes
    @param topic - (str)
    @param action - (str)
    @param key - (str) correlation ID
    @param value - (dict)
    @out - (bool)
    """

    now = timezone.now()

    data = value or {}

    if data.get("created_at", None):
        data["actual_created_at"] = data.pop("created_at")

    if data.get("updated_at", None):
        data["actual_updated_at"] = data.pop("updated_at")

    data.update(
        {
            settings.KAFKA_EVENT_ACTION_KEY: action,
            "correlation_id": str(key),
            "created_at": now.timestamp(),
        }
    )

    logger.info("send_event: Send event to Kafka", data=data)

    producer = create_producer()
    producer.produce(
        topic=topic, key=str(key), value=json.dumps(data), callback=log_event
    )
    producer.poll(1)

    logger.info("send_event: Success event to Kafka", data=data)
    return True


def activity_wallet_charge(*, key: str, value: dict):
    from core.services import wallet_charge

    res = wallet_charge(
        wallet_id=value["wallet_id"],
        amount=value["amount"],
        reference_id=value["reference_id"],
    )
    return res
