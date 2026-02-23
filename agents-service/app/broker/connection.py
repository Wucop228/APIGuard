import aio_pika

from app.core.config import settings

connection: aio_pika.abc.AbstractRobustConnection | None = None
channel: aio_pika.abc.AbstractChannel | None = None


async def connect_broker() -> None:
    global connection, channel

    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1, global_=True)

    print(f"Брокер подключился к RabbitMQ: {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}")


async def disconnect_broker() -> None:
    global connection, channel

    if connection and not connection.is_closed:
        await connection.close()

    connection = None
    channel = None

    print("Брокер отключился от RabbitMQ")