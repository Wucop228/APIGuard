import json

from aio_pika import IncomingMessage

from app.agents.registry import get_agent
from app.broker import connection as broker
from app.broker.constants import QUEUE_ANALYZE, QUEUE_GENERATE, QUEUE_REVIEW
from app.callback.client import send_result

QUEUE_TO_AGENT = {
    QUEUE_ANALYZE: "analyzer",
    QUEUE_GENERATE: "generator",
    QUEUE_REVIEW: "reviewer",
}


async def _process_task(queue_name: str, message: IncomingMessage) -> None:
    agent_type = QUEUE_TO_AGENT[queue_name]

    async with message.process():
        body = json.loads(message.body.decode())
        spec_id = body["spec_id"]

        print(f"Консюмер получил {agent_type} задачу: spec_id={spec_id}")

        agent = get_agent(queue_name)

        try:
            result = await agent.execute(body)

            await send_result(
                spec_id=spec_id,
                agent_type=agent_type,
                status="completed",
                content=result,
            )
            print(f"Консюмер выполнил задачу: spec_id={spec_id}, agent={agent_type}")

        except Exception as e:
            print(f"Консюмер получил ошибку: spec_id={spec_id}, agent={agent_type}, error={e}")

            await send_result(
                spec_id=spec_id,
                agent_type=agent_type,
                status="failed",
                error=str(e),
            )


async def start_consuming() -> None:
    if broker.channel is None:
        raise RuntimeError("Broker не подключен")

    for queue_name in QUEUE_TO_AGENT:
        queue = await broker.channel.declare_queue(queue_name, durable=True)
        await queue.consume(lambda msg, q=queue_name: _process_task(q, msg))
        print(f"Консюмер получает из очереди: {queue_name}")