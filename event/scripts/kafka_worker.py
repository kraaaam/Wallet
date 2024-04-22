import json
import logging

from confluent_kafka import Consumer, KafkaError, KafkaException, Message
from django.conf import settings
from django.utils import timezone
from django.utils.module_loading import import_string

from ..config import create_consumer

logger = logging.getLogger(__name__)


def _get_action(*, value: str):
    try:
        value = json.loads(value)
        return value.get(settings.KAFKA_EVENT_ACTION_KEY)
    except Exception as e:
        return value


def _get_functions(*, topic: str, action: str):
    topic_handler = settings.KAFKA_TOPIC_HANDLER.get(topic)

    if not topic_handler:
        return []

    fn_handler = topic_handler.get(action)

    if not fn_handler:
        return []

    return [i.lower().strip() for i in fn_handler.split(",")]


def _run_function(*, method: str, consumer: Consumer, message: Message) -> any:
    try:
        func = import_string(method)
        return func(
            consumer=consumer,
            message=message,
            # is_commit=not settings.KAFKA_ENABLE_AUTO_COMMIT,
        )
    except Exception as e:
        logger.exception(e)

        # if not settings.KAFKA_ENABLE_AUTO_COMMIT:
        #     consumer.commit(asynchronous=False)

    return True


def run():
    expiry_time = 1 * 60  # 1 minute
    start_time = timezone.now()
    topics = list(settings.KAFKA_TOPIC_HANDLER.keys())

    # https://docs.confluent.io/clients-confluent-kafka-python/current/overview.html#synchronous-commits
    try:
        print(f"Subscribing to {topics}...")

        consumer = create_consumer()
        consumer.subscribe(topics)
        msg_count = 0

        print(f"Subscribed to {topics}!")

        while True:
            print(f"Polling...")
            is_expired = (timezone.now() - start_time).total_seconds() > expiry_time
            msg = consumer.poll(timeout=1.0)

            if msg is not None:
                pass
            elif is_expired:
                break
            else:
                continue

            if msg.error() and msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                logger.warning(
                    f"%% {msg.topic()} [{msg.partition()}] reached end at offset {msg.offset()}"
                )
                continue
            elif msg.error():
                raise KafkaException(msg.error())

            action = _get_action(value=msg.value())
            functions = _get_functions(topic=msg.topic(), action=action)

            for function in functions:
                _run_function(method=function, consumer=consumer, message=msg)

            msg_count += 1

            # if settings.KAFKA_ENABLE_AUTO_COMMIT and (
            #     not (msg_count % settings.KAFKA_AUTO_COMMIT_COUNT) or is_expired
            # ):
            #     consumer.commit(asynchronous=False)

            if is_expired:
                break
    except Exception as e:
        print(f"Error: {e}")
        logger.exception(f"error : {e}")
    finally:
        # Close down consumer to commit final offsets.
        print(f"Closed connection")
        consumer.close()
