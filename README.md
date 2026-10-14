# Deribit Price Tracker

REST API сервис для отслеживания индексных цен BTC/USD и ETH/USD с биржи Deribit. Цены фетчатся каждую минуту через Celery и сохраняются в PostgreSQL.

## Стек

- **FastAPI** - REST API
- **Celery + Redis** - периодические задачи
- **PostgreSQL + SQLAlchemy (asyncpg)** - хранилище
- **aiohttp** - HTTP клиент для Deribit API
- **Alembic** - миграции
- **Docker Compose** - оркестрация сервисов

## Быстрый старт

```bash
cp .env.example .env
docker compose up --build
```

После запуска применить миграции:

```bash
docker compose exec app alembic upgrade head
```

API доступно на `http://localhost:8000`.

## Endpoints

| Метод | URL | Параметры | Описание |
|-------|-----|-----------|----------|
| GET | `/prices/` | `ticker` | Все цены по тикеру |
| GET | `/prices/latest` | `ticker` | Последняя цена по тикеру |
| GET | `/prices/range` | `ticker`, `from_ts`, `to_ts` | Цены за период (UNIX timestamps) |

Примеры запросов:

```bash
curl "http://localhost:8000/prices/?ticker=BTC_USD"
curl "http://localhost:8000/prices/latest?ticker=ETH_USD"
curl "http://localhost:8000/prices/range?ticker=BTC_USD&from_ts=1728800000&to_ts=1728900000"
```

## Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|-----------|----------|----------------------|
| `DATABASE_URL` | PostgreSQL DSN | `postgresql+asyncpg://postgres:postgres@localhost:5432/deribit_db` |
| `REDIS_URL` | Redis DSN | `redis://localhost:6379/0` |
| `DERIBIT_API_URL` | Базовый URL Deribit API | `https://www.deribit.com/api/v2` |
| `PRICE_FETCH_INTERVAL_SECONDS` | Интервал фетчинга в секундах | `60` |

## Запуск тестов

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## Структура проекта

```
app/
  api/          # FastAPI роуты и зависимости
  clients/      # aiohttp клиент для Deribit
  core/         # Конфиг (pydantic-settings)
  db/           # Сессия и базовый класс моделей
  models/       # SQLAlchemy модели
  repositories/ # Слой доступа к данным
  schemas/      # Pydantic схемы
  services/     # Бизнес-логика
  workers/      # Celery app и таски
alembic/        # Миграции базы данных
tests/          # Юнит-тесты
main.py         # Точка входа FastAPI
```

## Design decisions

**Слоистая архитектура (clients -> repositories -> services -> api)**

Каждый слой имеет одну ответственность. Это позволяет тестировать каждый слой изолированно через моки и легко заменять реализации — например, сменить Deribit на другую биржу достаточно в одном файле.

**Repository pattern**

Весь SQL изолирован в репозиториях. Сервисный слой работает только с доменными объектами и схемами, не зная о деталях хранилища. Базовый абстрактный класс `BaseRepository` задаёт контракт для всех репозиториев.

**Dependency Injection через FastAPI Depends**

Граф зависимостей (сессия -> репозиторий -> сервис) строится через `Depends` при каждом запросе. Никаких глобальных переменных. Это же позволяет подменять зависимости в тестах через `dependency_overrides`.

**Async стек (asyncpg + aiohttp)**

FastAPI асинхронный по природе, поэтому весь I/O (БД и HTTP) также async. Это даёт лучшую утилизацию потоков под нагрузкой без дополнительных воркеров.

**Celery Beat для планировщика**

Celery Beat запускается отдельным контейнером и отвечает только за расписание. Воркер — отдельный контейнер, он выполняет таски. Такое разделение позволяет масштабировать воркеры горизонтально не трогая beat.

**UNIX timestamp в БД**

Время хранится как `BigInteger` (UNIX timestamp). Это упрощает фильтрацию по диапазонам (обычное числовое сравнение) и убирает зависимость от таймзон на уровне БД.

**Pydantic Settings для конфига**

Все параметры окружения описаны в одном типизированном классе `Settings`. Нет разбросанных `os.getenv()` по коду, ошибка в имени переменной поймается при старте приложения.
