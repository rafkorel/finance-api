# Finance API

Finance API — мой учебный REST API на Python и FastAPI для учёта личных финансов. Я разрабатываю его, чтобы на практике освоить backend и подготовиться к стажировке или работе Junior Python Backend Developer. Начинал с хранения данных в словарях Python, затем перенёс их в PostgreSQL и добавил работу с курсами валют.

## Что реализовано

- **Счета и категории.** Создание, просмотр и удаление. Счета поддерживают RUB, USD и EUR. Категории разделены на доходы и расходы. Счёт или категорию со связанными записями удалить нельзя.
- **Доходы и расходы.** Операцию можно записать в валюте счёта или указать другую валюту. При конвертации сохраняю исходную сумму, сумму в валюте счёта, курс и его дату. При расходе проверяю остаток.
- **Переводы.** Можно переводить деньги между счетами в одинаковых и разных валютах. Сумма запроса задаётся в валюте отправителя. При отмене перевода или операции баланс корректируется по сохранённым суммам. Если отмена уведёт баланс в минус, API вернёт ошибку.
- **Курсы ЦБ РФ.** Получаю XML через HTTPX и разбираю его через ElementTree. Обрабатываю таймауты, ошибки HTTP и некорректные ответы ЦБ. Для операций в одной валюте внешний запрос не нужен.
- **Статистика.** Показываю балансы и суммы по категориям раздельно по валютам. Параметр `currency` позволяет пересчитать итог по актуальным курсам ЦБ. Также можно получить список операций за период.

Для денежных расчётов использую `Decimal`. Изменение балансов и запись операции выполняются в одной транзакции БД. Перед изменением блокирую нужные строки через `SELECT … FOR UPDATE`, чтобы одновременные запросы не списали одни и те же деньги.

## Стек и структура

Python 3.14, FastAPI, Pydantic 2, PostgreSQL 18, SQLAlchemy 2.0 с `AsyncSession`, psycopg, Alembic, HTTPX и Uvicorn. Для локального запуска PostgreSQL использую Docker.

```text
app/
├── api/v1/          # HTTP-маршруты
├── schemas/         # Валидация запросов
├── service/         # Бизнес-логика и конвертация валют
├── repository/      # Запросы к PostgreSQL
├── models/          # ORM-модели
├── integrations/    # Получение и разбор курсов ЦБ
├── core/            # Настройки
├── database.py      # Подключение и фабрика сессий
└── dependencies.py  # Сессия БД для запроса
migrations/          # Миграции Alembic
main.py              # Точка входа FastAPI
```

Запрос проходит через `Router → Service → Repository → Database`. Сервис конвертации обращается к ЦБ через отдельный модуль интеграции.

## Локальный запуск

Понадобятся Python 3.14, Git и PostgreSQL. Пример ниже подходит для Linux и пустой базы.

```bash
git clone https://github.com/rafkorel/finance-api.git
cd finance-api
python3.14 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

Если PostgreSQL ещё не запущен, его можно поднять через Docker.

```bash
docker run --name finance-postgres \
  -e POSTGRES_USER=finance \
  -e POSTGRES_PASSWORD=finance_dev \
  -e POSTGRES_DB=finance_db \
  -p 127.0.0.1:5432:5432 \
  -v finance_pgdata:/var/lib/postgresql \
  -d postgres:18
```

Когда PostgreSQL будет готов принимать подключения, создай `.env` из примера. Для своей базы укажи в нём подходящий `DATABASE_URL`.

```bash
cp .env.example .env
alembic upgrade head
uvicorn main:app --reload
```

Запросы можно отправлять из [Swagger UI](http://127.0.0.1:8000/docs).

## Эндпоинты

Общий префикс — `/api/v1`.

| Раздел | Методы и пути |
| --- | --- |
| Счета | `POST /accounts`, `GET /accounts`, `GET /accounts/{account_id}`, `DELETE /accounts/{account_id}` |
| Категории | `POST /categories`, `GET /categories`, `GET /categories/{category_id}`, `DELETE /categories/{category_id}` |
| Операции | `POST /transactions/income`, `POST /transactions/expense`, `GET /transactions`, `GET /transactions/{transaction_id}`, `DELETE /transactions/{transaction_id}` |
| Переводы | `POST /transfers`, `GET /transfers`, `GET /transfers/{transfer_id}`, `DELETE /transfers/{transfer_id}` |
| Статистика | `GET /statistics/balance`, `GET /statistics/categories`, `GET /statistics/period` |

Создай счёт в RUB и категорию типа `income`. Подставь их ID в запрос `POST /api/v1/transactions/income`.

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

На счёт поступит рублёвый эквивалент по курсу, доступному на момент запроса. Если опустить `currency`, сумма будет в валюте счёта. Поле `date` задаёт дату операции. Дата полученного курса хранится отдельно.

- `GET /api/v1/statistics/balance?currency=RUB` — общий баланс в рублях.
- `GET /api/v1/statistics/categories?category_type=expense` — расходы по категориям и исходным валютам. Чтобы получить пересчёт, добавь `&currency=RUB`.
- `GET /api/v1/statistics/period?date_from=2026-11-01&date_to=2026-11-30` — операции за ноябрь с включением обеих дат.

## Что дальше

Сейчас проект рассчитан на локальную работу с учебными данными. Основные сценарии можно проверить через Swagger. Авторизации и автоматических тестов в репозитории пока нет.

1. Покрыть основные сценарии тестами на `pytest` и запустить их в GitHub Actions. Параллельно попробовать BI-дашборд на данных проекта.
2. Добавить регистрацию, вход по JWT и доступ пользователя к своим данным. После этого рассмотреть простой интерфейс для демо.
3. Собрать API и PostgreSQL в Docker Compose, развернуть демо и настроить CD.
4. После рабочего демо попробовать добавить небольшую функцию на основе LLM.
