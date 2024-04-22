import json

from confluent_kafka import Consumer, Message
from django.utils import timezone

from .services import activity_wallet_charge


def stream_event_wallet_charge(
    *, consumer: Consumer, message: Message, is_commit: bool = True
) -> bool:
    """
    Sample method for consumer handling
    @param consumer - (Consumer)
    @param message - (Message)
    @out - (bool) if successful
    """

    now = timezone.localtime(timezone.now())

    # https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#message
    print(
        f"[{now}] Received {message.topic()} event ({message.key()}): {message.value()}"
    )

    activity_wallet_charge(
        key=message.key().decode(), value=json.loads(message.value().decode())
    )


    # https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#consumer
    if is_commit:
        consumer.commit(asynchronous=True)

    return True
