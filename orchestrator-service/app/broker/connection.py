import aio_pika
from aio_pika import ExchangeType

from app.core.config import settings
from app.broker.constants import (
    EXCHANGE_NAME,
    QUEUE_ANALYZE,
    QUEUE_GENERATE,
    QUEUE_REVIEW,
    ROUTING_KEY_ANALYZE,
    ROUTING_KEY_GENERATE,
    ROUTING_KEY_REVIEW,
)

connection: aio_pika.abc.AbstractRobustConnection | None = None
channel: aio_pika.abc.AbstractChannel | None = None
exchange: aio_pika.abc.AbstractExchange | None = None


async def connect_broker() -> None:
    global connection, channel, exchange

    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        EXCHANGE_NAME,
        ExchangeType.TOPIC,
        durable=True,
    )

    for queue_name, routing_key in [
        (QUEUE_ANALYZE, ROUTING_KEY_ANALYZE),
        (QUEUE_GENERATE, ROUTING_KEY_GENERATE),
        (QUEUE_REVIEW, ROUTING_KEY_REVIEW),
    ]:
        queue = await channel.declare_queue(queue_name, durable=True)
        await queue.bind(exchange, routing_key=routing_key)


async def disconnect_broker() -> None:
    global connection, channel, exchange

    if connection and not connection.is_closed:
        await connection.close()

    connection = None
    channel = None
    exchange = None


def get_exchange() -> aio_pika.abc.AbstractExchange:
    if exchange is None:
        raise RuntimeError("Broker не подключен")
    return exchange