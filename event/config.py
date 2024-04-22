from confluent_kafka import Consumer, Producer
from django.conf import settings

producer_conf = {
    "bootstrap.servers": settings.KAFKA_BROKER_URLS,
}

consumer_conf = {
    "bootstrap.servers": settings.KAFKA_BROKER_URLS,
    "group.id": settings.KAFKA_GROUP_ID,
    "auto.offset.reset": "earliest",
    "enable.auto.commit": settings.KAFKA_ENABLE_AUTO_COMMIT,
    # "message.max.bytes": 52428800,
}


def create_producer():
    """
    Create a producer instance with the given configuration
    """

    return Producer(producer_conf)


def create_consumer():
    """
    Create a consumer instance with the given configuration
    """

    return Consumer(consumer_conf)
