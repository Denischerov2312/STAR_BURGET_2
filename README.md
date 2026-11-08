# Сайт доставки еды Star Burger

Сайт сети ресторанов Star Burger, где можно заказать бургеры с доставкой на дом.

**Рабочий сайт:** [https://бургер67.bond](https://xn--67-9kcik8dcu.bond)

![скриншот сайта](https://dvmn.org/filer/canonical/1594651635/686/)

Сеть Star Burger объединяет несколько ресторанов с единым меню и ценами. Клиент выбирает блюда на сайте и указывает адрес, а менеджер видит заказ и ближайшие рестораны, которые могут его приготовить.

На сайте три интерфейса:

1. **Публичная часть** (`/`): меню и оформление заказа без регистрации.
2. **Панель менеджера** (`/manager/orders/`): обработка заказов, расстояние до ресторанов, способ оплаты и статус доставки.
3. **Панель администратора** (`/admin/`): меню ресторанов, категории товаров, пользователи и кэш геокодирования.

## Стек технологий

- **Бэкенд:** Python 3.12+, Django, Django REST Framework
- **Фронтенд:** React, Parcel
- **База данных:** PostgreSQL в продакшене, SQLite при локальной разработке
- **Сервер:** Nginx, Gunicorn, systemd, HTTPS от Let's Encrypt (Certbot)
- **Мониторинг ошибок:** Rollbar
- **Геокодирование:** API Яндекс.Карт

## Переменные окружения

Настройки читаются из файла `.env` в корне проекта, рядом с `manage.py`. Шаблон лежит в `.env.example`. Файл `.env` содержит секреты, его нельзя добавлять в репозиторий.

| Переменная | Обязательная | Описание | Пример |
| :--- | :--- | :--- | :--- |
| `SECRET_KEY` | да | Секретный ключ Django | `замените-на-длинную-случайную-строку` |
| `DEBUG` | нет | Режим отладки. По умолчанию `True`, в продакшене `False` | `False` |
| `ALLOWED_HOSTS` | нет | Домены через запятую. По умолчанию `127.0.0.1,localhost` | `example.com,www.example.com` |
| `DATABASE_URL` | нет | Подключение к базе. По умолчанию локальный SQLite | `postgres://user:password@localhost:5432/star_burger` |
| `YANDEX_GEOCODER_API_KEY` | нет | Ключ геокодера. Без него не считается расстояние до ресторанов | `ваш-ключ` |
| `ROLLBAR_TOKEN` | нет | Токен Rollbar со scope `post_server_item` | `ваш-токен` |
| `ROLLBAR_ENVIRONMENT` | нет | Название окружения в Rollbar. По умолчанию `development` | `production` |

## Локальный запуск

Нужны Python 3.12 или новее и Node.js. Бэкенд и фронтенд запускаются в двух разных терминалах.

### Бэкенд

Скачайте код:

```sh
git clone https://github.com/Denischerov2312/STAR_BURGET_2.git
cd STAR_BURGET_2
```

Создайте и активируйте виртуальное окружение:

```sh
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

Установите зависимости:

```sh
pip install -r requirements.txt
```

Создайте `.env` на основе `.env.example` и укажите в нём `SECRET_KEY` и `DEBUG=True`.

Примените миграции, создайте администратора и запустите сервер:

```sh
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

После установки база пустая. Рестораны, категории и товары добавляются в `/admin/`.

### Фронтенд

Во втором терминале установите JS-зависимости:

```sh
npm ci --include=dev
```

Запустите сборку с отслеживанием изменений:

```sh
# Linux / macOS
./node_modules/.bin/parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"

# Windows
.\node_modules\.bin\parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
```

Сайт откроется по адресу [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Деплой на сервер

Проект развёрнут на Ubuntu 24.04. Nginx принимает запросы, сам отдаёт `/static/` и `/media/`, остальное передаёт в Gunicorn на `127.0.0.1:8000`.

Для первого развёртывания:

1. Установите PostgreSQL, Nginx и Node.js, клонируйте репозиторий, создайте `venv` и установите зависимости.
2. Создайте `.env` с `DEBUG=False`, `DATABASE_URL`, `ALLOWED_HOSTS`, ключами сервисов и закройте его от других пользователей: `chmod 600 .env`.
3. Настройте службу `gunicorn` в systemd и сайт в Nginx.
4. Получите HTTPS-сертификат:

```sh
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d ваш-домен -d www.ваш-домен
```

Сертификат продлевается автоматически. Проверить продление можно командой `sudo certbot renew --dry-run`.

### Обновление сайта

Обновление выполняет скрипт `~/deploy.sh` на сервере. Он останавливается при первой ошибке и выполняет следующие шаги:

```sh
cd ~/STAR_BURGET_2
git pull
source venv/bin/activate
pip install -r requirements.txt
NODE_OPTIONS=--no-experimental-fetch ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
python manage.py migrate --noinput
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

## Цели проекта

Код написан в учебных целях: это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org). За основу взят код проекта [FoodCart](https://github.com/Saibharath79/FoodCart).
