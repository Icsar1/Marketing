# SEO Lead Analyzer (Tilda + Yandex APIs)

Легкий сервис для VPS:
- принимает заявку с Tilda через webhook,
- делает SEO-экспресс анализ,
- отдает результат по случайной ссылке,
- хранит отчет 3 дня (по умолчанию) и удаляет автоматически.

## Ключевой вопрос: можно ли сделать это только на Yandex Direct API?

Коротко: **нет, не полностью**.

`Yandex Direct API` — это API рекламной платформы. Он полезен для оценки рекламного спроса/семантики,
но **не дает полного SEO-аудита** (индексация, техошибки сайта, видимость по органике, конкурентные SEO-gaps).

Для полноценного отчета нужен **гибрид**:
- `Yandex Webmaster API` — индексация и технические проблемы;
- `Yandex Metrica API` — поведенка и конверсионные сигналы;
- внешний SEO/serp-источник для сравнения с конкурентами и keyword gaps.

## Российская альтернатива DataForSEO

Если нужна именно российская альтернатива, практичный вариант:
- **Topvisor API** — российский сервис, который удобно использовать для позиций/видимости/сравнения с конкурентами.

Рабочая связка для РФ-рынка:
1. `Yandex Webmaster API` + `Yandex Metrica API`;
2. `Topvisor API` для конкурентной SEO-видимости и позиций;
3. при необходимости `Yandex Direct API` как доп. источник по коммерческому спросу.

> В проекте для этого добавлен режим `SEO_DATA_PROVIDER=russian_seo` (каркас интеграции).

## Что обещаем на лендинге

**Покажем за 30 минут, почему сайт не приносит заявки**
- ✔ Проверим критические ошибки
- ✔ Оценим потенциал трафика и спрос в нише
- ✔ Покажем слабые места относительно конкурентов
- ✔ Скажем, как увеличить заявки и заказы

## Почему не PDF по умолчанию

Можно делать PDF (например через WeasyPrint/wkhtmltopdf), но это добавляет вес и зависимости.
Чтобы сервис оставался легким, сейчас используется компромисс:
- отчет публикуется на отдельной странице `/r/<uuid>`;
- страница живет `72` часа (настраивается);
- затем автоматически удаляется.

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Пример env

```env
APP_BASE_URL=https://your-domain.ru
REPORT_TTL_HOURS=72
DB_PATH=seo_reports.db

# mock | yandex_hybrid | russian_seo
SEO_DATA_PROVIDER=mock

YANDEX_WEBMASTER_TOKEN=
YANDEX_DIRECT_TOKEN=
YANDEX_METRICA_TOKEN=
TOPVISOR_API_KEY=
```

## Интеграция с Tilda

В Tilda отправляйте POST на:

`/webhooks/tilda/seo`

JSON:

```json
{
  "name": "Иван",
  "phone": "+79990000000",
  "email": "mail@example.com",
  "site_url": "https://example.com"
}
```

Ответ:

```json
{
  "message": "SEO отчет создан",
  "report_url": "https://your-domain.ru/r/<uuid>",
  "expires_at": "2026-01-01T10:00:00+00:00"
}
```

## Архитектура провайдеров данных

В `app/providers.py`:
- `MockSeoDataProvider` — локальная заглушка;
- `YandexHybridProvider` — контур варианта (Webmaster + Metrica + Direct + внешний SEO API);
- `RussianSeoProvider` — контур для РФ-стека (Webmaster + Metrica + Topvisor API).

Выбор провайдера делается через `SEO_DATA_PROVIDER`.

## API

- `GET /health` — healthcheck.
- `POST /webhooks/tilda/seo` — вход для заявок.
- `GET /r/{report_id}` — страница отчета.
