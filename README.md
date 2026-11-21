# Finance API

Учебное REST API для учёта личных финансов на **Python и FastAPI**. Проект развивается как практическая подготовка к стажировке или позиции Junior Python Backend Developer: от CRUD и PostgreSQL до многовалютных операций, автоматических тестов и аналитического дашборда.

## Возможности

- **Счета:** RUB, USD, EUR; создание, получение, список и удаление с проверкой связанных записей.
- **Категории:** доходы и расходы; создание, получение и удаление.
- **Операции:** доходы и расходы в валюте счёта или указанной валюте с пересчётом; проверка достаточности средств; отмена с обратным изменением баланса.
- **Переводы:** между счетами одной или разных валют; при отмене используются сохранённые суммы.
- **Курсы ЦБ РФ:** загрузка XML через HTTPX, разбор через ElementTree; обработка ошибок внешнего API. Сохраняются исходная и зачисленная суммы, курс, дата курса и источник.
- **Статистика:** балансы, суммы по категориям и операции за период. Суммы можно смотреть по валютам или пересчитать в выбранную валюту по актуальным курсам.
- **BI:** отдельная демонстрационная PostgreSQL, SQL-запросы и Metabase-дашборд с фильтрами даты и валюты.
- **Проверка качества:** unit- и интеграционные тесты с pytest; GitHub Actions запускает тесты с PostgreSQL и миграциями Alembic.

Для денежных значений используется `Decimal`. Изменение балансов и создание/удаление финансовой записи выполняются в одной транзакции. `SELECT … FOR UPDATE` блокирует строки счетов при изменениях; при переводе счета блокируются в порядке ID.

## Технологии

Python 3.14 · FastAPI · Pydantic 2 · PostgreSQL 18 · SQLAlchemy 2.0 (`AsyncSession`) · psycopg · Alembic · HTTPX · pytest · GitHub Actions · Docker (PostgreSQL) · Metabase · SQL.

## Архитектура

```text
Router → Service → Repository → Database
                       └── PostgreSQL
Service → Currency Service → CBR Integration
```

```text
app/
├── api/v1/          # HTTP-маршруты
├── schemas/         # Pydantic-схемы запросов
├── service/         # Бизнес-логика, валюты и статистика
├── repository/      # Доступ к данным
├── models/          # SQLAlchemy ORM
├── integrations/    # HTTPX + разбор XML ЦБ РФ
├── core/            # Настройки
├── tests/           # Unit- и интеграционные тесты
├── database.py      # Движок и фабрика сессий
└── dependencies.py  # Зависимость сессии БД
bi/                  # Демоданные, SQL, скриншоты и инструкция Metabase
migrations/          # Alembic
scripts/test.sh      # Локальный запуск тестов через .env.test
.github/workflows/   # GitHub Actions CI
main.py              # FastAPI-приложение
```

## Запуск API локально

Нужны **Python 3.14**, Git и PostgreSQL. Ниже — пример для Linux с PostgreSQL 18 в Docker.

```bash
git clone https://github.com/rafkorel/finance-api.git
cd finance-api
python3.14 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

Запусти PostgreSQL (если соответствующий контейнер ещё не создан):

```bash
docker run --name finance-postgres \
  -e POSTGRES_USER=finance \
  -e POSTGRES_PASSWORD=finance_dev \
  -e POSTGRES_DB=finance_db \
  -p 127.0.0.1:5432:5432 \
  -v finance_pgdata:/var/lib/postgresql \
  -d postgres:18
```

После готовности PostgreSQL:

```bash
cp .env.example .env
python -m alembic upgrade head
python -m uvicorn main:app --reload
```

При необходимости исправь `DATABASE_URL` в `.env`. Swagger UI: **http://127.0.0.1:8000/docs**.

## Основные маршруты

Общий префикс: `/api/v1`.

| Раздел | Методы и пути |
| --- | --- |
| Счета | `POST /accounts`, `GET /accounts`, `GET /accounts/{account_id}`, `DELETE /accounts/{account_id}` |
| Категории | `POST /categories`, `GET /categories`, `GET /categories/{category_id}`, `DELETE /categories/{category_id}` |
| Операции | `POST /transactions/income`, `POST /transactions/expense`, `GET /transactions`, `GET /transactions/{transaction_id}`, `DELETE /transactions/{transaction_id}` |
| Переводы | `POST /transfers`, `GET /transfers`, `GET /transfers/{transfer_id}`, `DELETE /transfers/{transfer_id}` |
| Статистика | `GET /statistics/balance`, `GET /statistics/categories`, `GET /statistics/period` |

### Пример дохода в валюте, отличной от валюты счёта

Сначала создай счёт в RUB и категорию `income`. Затем подставь их ID:

```http
POST /api/v1/transactions/income
Content-Type: application/json
```

```json
{
  "account_id": 1,
  "category_id": 1,
  "amount": "100.00",
  "currency": "USD",
  "date": "2026-11-13",
  "description": "Пример дохода в долларах"
}
```

Сумма зачисления рассчитывается в валюте счёта. Если не передать `currency`, используется валюта счёта. Дата операции и дата курса хранятся отдельно. Запросы на конвертацию разных валют зависят от доступности ответа ЦБ.

Примеры статистики:

- `GET /api/v1/statistics/balance?currency=RUB`
- `GET /api/v1/statistics/categories?category_type=expense`
- `GET /api/v1/statistics/categories?category_type=expense&currency=RUB`
- `GET /api/v1/statistics/period?date_from=2026-11-01&date_to=2026-11-30`

## Тестирование

Используются **pytest** и **HTTPX ASGITransport**. Unit-тесты проверяют валютную конвертацию, округление и XML ЦБ. Интеграционные тесты выполняют HTTP-запросы к FastAPI и проверяют изменения в PostgreSQL (счета, доходы, расходы, переводы и типовые ошибки). Для тестирования ответа ЦБ используется `MockTransport`, а не реальная сеть.

Unit-тесты конвертации и XML не требуют подключения к PostgreSQL:

```bash
python -m pytest app/tests/unit -v
```

**Интеграционные тесты — только на отдельной базе `finance_api_test`.** Создай эту базу в PostgreSQL и локальный файл `.env.test` (не добавляй его в Git):

```env
DATABASE_URL=postgresql+psycopg://finance_test:finance_test@localhost:5432/finance_api_test
```

В качестве примера использованы тестовые имя пользователя и пароль; создай соответствующую роль и базу либо подставь свои данные. Примени миграции именно к тестовой базе и запусти проверки:

```bash
(
  set -a
  source .env.test
  set +a
  python -m alembic upgrade head
)
bash scripts/test.sh -v
```

`app/tests/integration/conftest.py` дополнительно проверяет имя подключённой базы, чтобы тесты не запускались на основной БД. Текущие интеграционные тесты создают записи и очищают их после проверки; пока не следует использовать для тестов базу с ценными данными.

### CI и работа с ветками

Workflow: [`.github/workflows/tests.yml`](.github/workflows/tests.yml). В GitHub Actions поднимается PostgreSQL 18, устанавливаются зависимости, применяются миграции, затем выполняется `python -m pytest app/tests -v`.

Сейчас автоматический запуск настроен:

- на `push` в `main` и `test/pytest-ci`;
- на **pull request в `main` из любой ветки**.

**Принятый процесс разработки:** из всех прочих веток (например, `feat/bi-dashboard`, `feat/jwt-auth`) изменения добавляются в `main` **только через Pull Request** после успешного CI. Прямое слияние на локальном компьютере с последующим `push main` обходит предварительную проверку PR и не используется для этих веток. Для технического запрета прямых слияний необходимо отдельно настроить GitHub Ruleset / защиту ветки `main` с обязательной проверкой CI; сам workflow пока не запрещает обход.

## BI-дашборд

В Metabase реализован учебный дашборд по доходам, расходам и переводам: показатели по категориям и месяцам, чистый денежный поток и фильтры периода/валюты.

Дашборд использует **отдельную базу `finance_api_bi`** с демонстрационными данными и пользователя PostgreSQL с правами только на чтение. Разные валюты не смешиваются в одной сумме; для аналитики используются исходные суммы операций, переводы учитываются отдельно. API для открытия дашборда запускать не требуется.

**[Инструкция, SQL-запросы и скриншоты](bi/README.md)**.

## Ограничения и дальнейшие планы

Finance API — учебный проект на локальных тестовых данных, а не готовая финансовая система. Авторизация и разграничение доступа между пользователями пока не реализованы.

Ближайшие задачи: расширение полезных тестовых сценариев и BI-практики, затем пользователи и JWT, Docker Compose для API и БД, деплой и CD. После готового демо — небольшие эксперименты с LLM. Redis, Kafka и Kubernetes не входят в обязательный план без конкретной задачи.
