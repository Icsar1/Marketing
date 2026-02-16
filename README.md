# SEO Lead Analyzer (Tilda + Yandex API-ready)

Легкий сервис для VPS:
- принимает заявку с Tilda через webhook,
- делает SEO-экспресс анализ (каркас под Yandex API),
- отдает результат по случайной ссылке,
- хранит отчет 3 дня (по умолчанию) и удаляет автоматически.

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
YANDEX_WEBMASTER_TOKEN=
YANDEX_DIRECT_TOKEN=
YANDEX_METRICA_TOKEN=
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

## Что подключить для реального Yandex API

В `app/seo_service.py` есть пометки, куда добавить:
- Яндекс Вебмастер API (ошибки индексирования, технические проблемы),
- Метрика API (поведенческие сигналы),
- Данные спроса через Yandex Direct/Wordstat-совместимый слой.

## API

- `GET /health` — healthcheck.
- `POST /webhooks/tilda/seo` — вход для заявок.
- `GET /r/{report_id}` — страница отчета.
