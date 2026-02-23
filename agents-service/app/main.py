import asyncio
import signal

from app.agents.registry import register_all
from app.broker.connection import connect_broker, disconnect_broker
from app.broker.consumer import start_consuming
from app.callback.client import init_http_client, close_http_client


async def main():
    print("Запуск agents-service")

    await init_http_client()
    register_all()
    await connect_broker()
    await start_consuming()

    print("Сервис запущен")

    stop_event = asyncio.Event()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await stop_event.wait()

    print("Завершение")
    await disconnect_broker()
    await close_http_client()
    print("Все завершено")


if __name__ == "__main__":
    asyncio.run(main())