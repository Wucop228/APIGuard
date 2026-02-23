from app.agents.base import BaseAgent

_registry: dict[str, BaseAgent] = {}


def register(queue_name: str, agent: BaseAgent) -> None:
    _registry[queue_name] = agent
    print(f"Зарегистрирован агент '{agent.name}' для очереди '{queue_name}'")


def get_agent(queue_name: str) -> BaseAgent:
    agent = _registry.get(queue_name)
    if agent is None:
        raise ValueError(f"Нет агента для очереди: {queue_name}")
    return agent


def register_all() -> None:
    from app.agents.analyzer.agent import AnalyzerAgent
    from app.agents.generator.agent import GeneratorAgent
    from app.agents.reviewer.agent import ReviewerAgent
    from app.broker.constants import QUEUE_ANALYZE, QUEUE_GENERATE, QUEUE_REVIEW

    register(QUEUE_ANALYZE, AnalyzerAgent())
    register(QUEUE_GENERATE, GeneratorAgent())
    register(QUEUE_REVIEW, ReviewerAgent())