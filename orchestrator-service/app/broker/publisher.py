import json

import aio_pika

from app.broker.connection import get_exchange


async def publish_task(routing_key: str, payload: dict) -> None:
    exchange = get_exchange()

    message = aio_pika.Message(
        body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        content_type="application/json",
    )

    await exchange.publish(message, routing_key=routing_key)