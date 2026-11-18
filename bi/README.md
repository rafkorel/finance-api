# BI-дашборд Finance API

Для практики BI-разработки я сделал небольшой дашборд на основе своего проекта Finance API.

Для этого использовал PostgreSQL, SQL и Metabase.

Дашборд позволяет посмотреть доходы, расходы и переводы между счетами.

## Что показывает дашборд

- Общие доходы.
- Общие расходы.
- Чистый денежный поток (доходы минус расходы).
- Доходы по категориям.
- Расходы по категориям.
- Доходы и расходы по месяцам.
- Переводы между счетами.

Также можно выбрать период и валюту (RUB, USD или EUR).

Для расчётов используются суммы в исходной валюте операции. Разные валюты между собой не складываются.

Переводы между своими счетами показываются отдельно и не учитываются как доходы или расходы.

## Как это работает

Metabase подключается напрямую к PostgreSQL и выполняет SQL-запросы.

Для BI я создал отдельную базу `finance_api_bi`, чтобы не использовать данные из основной базы проекта.

В неё добавил тестовые счета, категории, операции и переводы за 2026 год.

Для подключения Metabase создал пользователя `metabase_reader`, которому разрешено только читать данные.

FastAPI для работы дашборда не нужен.

## Как запустить

Для запуска понадобятся PostgreSQL, Docker и Metabase.

### 1. Создать базу данных

Подключись к PostgreSQL и создай базу.

```sql
CREATE DATABASE finance_api_bi;
```

### 2. Создать таблицы

Для создания таблиц используются миграции Alembic из основного проекта.

Создай `.env.bi` в корне проекта и добавь подключение к новой базе.

```env
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/finance_api_bi
```

Вместо `postgres` и `password` укажи свои данные PostgreSQL.

Из корня проекта с активированным `venv` выполни:

```bash
(
    set -a
    source .env.bi
    set +a
    alembic upgrade head
)
```

### 3. Добавить демонстрационные данные

Открой файл [`bi/demo_data.sql`](demo_data.sql) в DBeaver. Выбери подключение к `finance_api_bi` и выполни SQL-скрипт целиком.

Скрипт сначала проверяет имя базы и что таблицы пустые. Затем добавляет счета и категории с готовыми ID. Эти же ID используются в операциях и переводах, поэтому подставлять их вручную не нужно.

Повторно запускать скрипт после добавления данных не нужно.

### 4. Создать пользователя для Metabase

Подключись к `finance_api_bi` и выполни команды. Если роль `metabase_reader` уже есть, пропусти `CREATE ROLE`.

```sql
CREATE ROLE metabase_reader LOGIN PASSWORD 'your_password';

GRANT CONNECT ON DATABASE finance_api_bi TO metabase_reader;
GRANT USAGE ON SCHEMA public TO metabase_reader;

GRANT SELECT ON
    accounts,
    categories,
    transactions,
    transfers
TO metabase_reader;
```

Так Metabase сможет получать данные, но не сможет их изменять.

### 5. Запустить Metabase

Я запускал Metabase в отдельном Docker-контейнере на Ubuntu.

```bash
docker run -d \
    --name finance-metabase \
    --network host \
    -e MB_JETTY_HOST=127.0.0.1 \
    -e MB_DB_FILE=/metabase-data/metabase.db \
    -v finance_metabase_data:/metabase-data \
    metabase/metabase:v0.65.3.x
```

После запуска открой [Metabase](http://127.0.0.1:3000).

### 6. Подключить PostgreSQL

В настройках Metabase добавь базу PostgreSQL.

| Параметр | Значение |
|---|---|
| Host | `127.0.0.1` |
| Port | `5432` |
| Database | `finance_api_bi` |
| Username | `metabase_reader` |
| Password | Пароль пользователя |

После подключения Metabase сможет получать данные из таблиц Finance API.

## SQL-запросы

Все SQL-запросы, которые я использовал для создания графиков, находятся в папке [`bi/queries/`](queries/).

С помощью этих запросов рассчитываются доходы, расходы, чистый денежный поток и переводы.

Для построения графиков я использовал возможности Metabase.

Фильтры даты и валюты настроены через переменные SQL-запросов.

Готовый дашборд собирается в интерфейсе Metabase из сохранённых запросов.

## Скриншоты

### Основной дашборд

![Finance API Dashboard](screenshots/dashboard-rub.png)

### Пример фильтрации по USD

![Finance API Dashboard USD](screenshots/dashboard-usd-october.png)

<sub>Дашборд использует только учебные данные.</sub>