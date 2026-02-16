# SEO Lead Analyzer (VPS-first)

Сервис для VPS, который:
- принимает заявку в API,
- делает SEO-экспресс анализ,
- выдает ссылку на отчет,
- удаляет отчет через 3 дня.

## С чего начать (без Tilda)

Сначала просто подними сервис на VPS и проверь, что он работает.

### 1) Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2) Проверка здоровья сервиса

Открой:

`http://<VPS_IP>:8000/health`

Должен вернуться JSON со статусом `ok`.

### 3) Создание тестового отчета (вручную)

```bash
curl -X POST http://<VPS_IP>:8000/lead/seo \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Иван",
    "phone": "+79990000000",
    "email": "mail@example.com",
    "site_url": "https://example.com"
  }'
```

В ответе придет `report_url`.

### 4) Открытие отчета

Открой `report_url` в браузере.

---

## Когда VPS уже работает, подключаем Tilda

В Tilda нужно будет отправлять POST-запрос на:

`http://<VPS_IP>:8000/lead/seo`

(Потом заменишь на домен/HTTPS, когда будет готово.)

---

## Пример env

```env
APP_BASE_URL=http://<VPS_IP>:8000
REPORT_TTL_HOURS=72
DB_PATH=seo_reports.db

# mock | yandex_hybrid | russian_seo
SEO_DATA_PROVIDER=mock

YANDEX_WEBMASTER_TOKEN=
YANDEX_DIRECT_TOKEN=
YANDEX_METRICA_TOKEN=
TOPVISOR_API_KEY=
```


## Как забрать проект на VPS через GitHub (без постоянных скачиваний)

Если сервер «не знает git», сначала установи его:

```bash
sudo apt update
sudo apt install -y git
```

Дальше один раз клонируешь проект:

```bash
cd /opt
sudo git clone https://github.com/<your-user>/<your-repo>.git seo-analyzer
cd seo-analyzer
```

После этого для обновлений не нужно скачивать ZIP. Достаточно:

```bash
cd /opt/seo-analyzer
git pull
```

Если работаешь не из `main`, а из ветки (например `work`), переключись на неё:

```bash
git fetch --all
git checkout work
git pull origin work
```

## API

- `GET /health` — проверка, что сервис жив.
- `POST /lead/seo` — создать SEO-отчет.
- `GET /r/{report_id}` — страница отчета.

## Если в консоли VPS ошибка `Invalid regular expression`

На некоторых VPS (busybox/урезанный grep) команда с экранированием может падать:

```bash
grep -n "list\\[" app/models.py app/providers.py
```

Используй один из совместимых вариантов:

```bash
grep -nF "list[" app/models.py app/providers.py
```

или:

```bash
rg -n "list\\[" app/models.py app/providers.py
```
