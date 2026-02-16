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

Одна строка = одна команда. Не склеивай несколько команд в одну строку.

```bash
sudo apt update
sudo apt install -y git
```

Дальше один раз клонируешь проект.

⚠️ ВАЖНО: `<your-user>` и `<your-repo>` — это шаблон. Вставь реальный URL репозитория.
Для этого проекта пример такой:

```bash
cd /opt
sudo git clone https://github.com/Icsar1/Marketing.git seo-analyzer
cd seo-analyzer
```

Если репозиторий приватный — используй URL своего приватного репо и авторизацию (token/SSH).

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


## Частая ошибка: `{"detail":"Method Not Allowed"}`

Это не критичная ошибка сервера. Обычно значит, что в `/lead/seo` ушёл **GET**, а endpoint ждёт только **POST**.

Проверь так (одной строкой, без переносов):

```bash
curl -X POST "http://<VPS_IP>:8000/lead/seo" -H "Content-Type: application/json" -d '{"name":"Иван","phone":"+79990000000","email":"mail@example.com","site_url":"https://example.com"}'
```

Если в логе снова `GET /lead/seo 405`, значит команда `curl` была вставлена с ошибкой/переносом и shell отправил не тот запрос.

## Нужно ли сначала создавать webhook в Tilda?

Да. Сначала подними и проверь API на VPS, потом в Tilda создай webhook:

- Webhook URL: `http://<VPS_IP>:8000/lead/seo`
- Method: `POST`
- API NAME / API KEY: пока можно оставить пустыми

Мини-порядок:
1. Запустить `uvicorn` на VPS.
2. Проверить `GET /health`.
3. Проверить `POST /lead/seo` через `curl`.
4. Только после этого подключать форму Tilda к этому URL.

## API

- `GET /health` — проверка, что сервис жив.
- `POST /lead/seo` — создать SEO-отчет.
- `GET /r/{report_id}` — страница отчета.

## Если при запуске ошибка `TypeError: 'type' object is not subscriptable`

Это значит, что на VPS крутится **старая версия файлов** с аннотациями `list[str]` (Python 3.8 так не умеет).

Сделай по шагам:

```bash
cd /opt/seo-analyzer
git fetch --all
git checkout work
git pull origin work
python -m compileall app
```

Проверь, что в файлах больше нет `list[`:

```bash
grep -nF "list[" app/models.py app/providers.py
```

Если команда ничего не вывела — всё ок, запускай:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Если `list[` всё ещё есть, принудительно обнови 2 файла из git:

```bash
git checkout -- app/models.py app/providers.py
python -m compileall app
```


### Экстренный фикс прямо на VPS (если `git pull` не помог)

Выполни команды ниже по одной строке в папке проекта:

```bash
cd /opt/seo-analyzer
sed -i 's/list\[str\]/List[str]/g; s/list\[dict\]/List[Dict[str, str]]/g' app/models.py app/providers.py
grep -q "from typing import Dict, List" app/models.py || sed -i '1i from typing import Dict, List' app/models.py
grep -q "from typing import Dict, List" app/providers.py || sed -i '1i from typing import Dict, List' app/providers.py
python -m compileall app
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Проверка (должно быть пусто):

```bash
grep -nF "list[" app/models.py app/providers.py
```

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
