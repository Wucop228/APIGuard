# APIGuard

Сервис для автоматической генерации pytest тестов по openapi спецификации при помощи LLM. Микросервисная архитектура, мультиагентный пайплайн с RAG

## Архитектура

Проект состоит из 4 сервисов:

- **gateway** (порт 8080) - точка входа, проксирует запросы к внутренним сервисам, добавляет `user_id` и `X-Request-ID` в запросы, пробрасывает cookies
- **auth-service** (порт 8000) - регистрация, аутентификация, JWT через httpOnly cookies с refresh token
- **orchestrator-service** (порт 8001) - валидация и парсинг openapi спецификаций, координация агентов, хранение результатов
- **agents-service** - мультиагентная система, слушает RabbitMQ, выполняет задачи и отправляет результаты в оркестратор

## Пайплайн

```
OpenAPI upload => Validator => Parser => RabbitMQ => Analyzer => Generator => Reviewer => Результат
```

Три агента, каждый со своей ролью:

1. **Analyzer** - анализирует распарсенную спецификацию и формирует тест план: эндпоинты, сценарии (positive, negative, edge_case, auth), приоритеты, примеры данных
2. **Generator** - генерирует pytest код по тест плану
3. **Reviewer** - проверяет качество сгенерированных тестов с использованием RAG, выставляет оценку, находит проблемы и выдаёт улучшенную версию кода

Агенты общаются через RabbitMQ. Оркестратор получает результаты через callback эндпоинт и запускает следующий этап пайплайна

## RAG в Reviewer

Перед ревью Reviewer ищет в базе знаний (ChromaDB) релевантные правила и паттерны, а затем добавляет их в промпт LLM как контекст. База знаний содержит best practices для pytest

Эмбеддинги генерируются локально с помощью модели `paraphrase-multilingual-MiniLM-L12-v2`. База инициализируется при старте из `knowledge.json`

## Стек

- Python, FastAPI, async SQLAlchemy, PostgreSQL, Alembic
- RabbitMQ (aio-pika) - брокер сообщений между оркестратором и агентами
- OpenAI SDK - вызовы LLM через NVIDIA API (DeepSeek, Qwen)
- ChromaDB, LangChain (Chroma, HuggingFace, Text Splitters) - RAG для Reviewer
- Docker, docker-compose
- httpx - http клиент в gateway и в agents-service

## Запуск

```bash
# Скопировать .env.example => .env для каждого сервиса и корневой директории
make up        # Поднять все сервисы
make migrate   # Применить миграции
make logs      # Логи всех сервисов
```

Команды для отдельных сервисов:

```bash
make logs-auth          # Логи auth-service
make logs-orchestrator  # Логи orchestrator-service
make logs-agents        # Логи agents-service
make logs-gateway       # Логи gateway
make clean              # Остановить и удалить volumes
```

## API

Регистрация и логин:

```bash
curl -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}' \
  -c cookies.txt
```

Загрузка спецификации:

```bash
jq -Rs '{content: .}' spec.json | curl -X POST http://localhost:8080/spec/upload \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d @-
```

Проверка статуса и получение результатов:

```bash
curl http://localhost:8080/spec/<spec_id>/status -b cookies.txt
curl http://localhost:8080/spec/<spec_id>/results -b cookies.txt
```

## Структура проекта

```
APIGuard/
  gateway/                  # API Gateway (FastAPI, порт 8080)
    app/
      middleware/            # AuthMiddleware, RequestIdMiddleware
      routers/               # auth, spec, health
      dependencies/          # get_current_user, get_optional_user

  auth-service/             # Аутентификация (FastAPI, порт 8000)
    app/
      auth/                  # JWT, refresh tokens, bcrypt
      user/                  # Модель User, регистрация

  orchestrator-service/     # Оркестратор (FastAPI, порт 8001)
    app/
      spec/                  # Validator, Parser, Service, DAO
      broker/                # RabbitMQ publisher, exchange/queue setup

  agents-service/           # AI агенты
    app/
      agents/
        analyzer/            # Анализ спеки => тест план
        generator/           # Тест план => pytest код
        reviewer/            # Ревью + RAG => улучшенный код
      broker/                # RabbitMQ consumer
      callback/              # HTTP клиент для отправки результатов
      rag/                   # ChromaDB store, retriever, knowledge.json
      llm/                   # OpenAI SDK клиент, JSON parser

  docker-compose.yml
  init-db.sh                # Инициализация двух PostgreSQL БД
  Makefile
```