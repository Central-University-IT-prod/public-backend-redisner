# [<img src="https://img.shields.io/badge/Telegram-%40TravelWithIvesBot-blue">](https://t.me/TravelWithIvesBot) [<img src="https://img.shields.io/badge/Заключительный этап-PROD 2024-darkgreen">](https://prodcontest.ru)

# Travel Agent 3.0

## Описание

Telegram бот, предназначенный для помощи в планировании совместных
путешествий

## Как найти бота

Бот доступен по ссылке [@TravelWithIvesBot](https://t.me/TravelWithIvesBot)

Единственный доступный на данный момент язык — русский

## [Как пользоваться ботом](readme/how-to-use.md)

## Используемые технологии

- [aiogram](https://github.com/aiogram/aiogram) — фреймворк для асинхронного взаимодействия с [Telegram Bot API](https://core.telegram.org/bots/api)
- [redis](https://redis.io/) — хранение данных; используется для удобной работы с FSM в aiogram
- [Docker](https://www.docker.com/) и [Docker-Compose](https://docs.docker.com/compose) — быстрый запуск проекта в контейнерах
- [PostgreSQL](https://www.postgresql.org/) — гибкая, многофункциональная и масштабируемая СУБД для управления данными о пользователях, путешествиях и прочими необходимыми для бота данными
- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) — ORM для удобного взаимодействия с СУБД 

## [Схема данных СУБД](readme/database.md)

## Внешние интеграции

- [Foursquare API](https://location.foursquare.com/developer/docs-home) — API с условно-бесплатным доступом, предоставляет простой поиск интересных мест и достопримечательностей по всему миру
- [Nominatim](https://nominatim.openstreetmap.org/ui/about.html) — поисковая система для OpenStreetMap
- [OpenWeatherMap](https://openweathermap.org/api) — API с бесплатным доступом для части запросов, позволяет получить прогноз погоды на ближайшие дни

## Структура проекта

- ### Docker
	- `Dockerfile` — установка Python 3.12 и всех необходимых зависимостей из `requirements.txt`
	- `docker-compose.yml` (список сервисов):
		- `postgres` — инициализация СУБД PostgreSQL 14.5 с пустой базой данных
		- `redis` — инициализация СУБД Redis
		- `bot` — запуск скрипта `__main__.py` в корневой папке проекта
- ### Вспомогательные файлы
	- `.env` — хранение переменных окружения, таких как API токены для Telegram и внешних интеграций
	- `requirements.txt` — список зависимостей для установки при запуске `Dockerfile`
    - `localization/` — локализация бота
      - `locales/**.yaml` — структурированный файл со связями вида `псевдоним_строки: строка`
- ### Python
	- `__main__.py` — основной скрипт, запускающий бота
	- `config.py` — управление переменными окружения
	- `assistive/` — вспомогательные скрипты
		- `callback.py` — объекты `CallbackData` для передачи в inline-кнопки под сообщениями бота
		- `states.py` — объекты `StatesGroup` для работы с FSM и хранения состояний пользователей
		- `processors.py` — функции-обработчики, позволяющие преобразовать "сырые" объекты в тексты и клавиатуры для сообщений
	- `database/` — скрипты, относящиеся к хранению и управлению данными
		- `models.py` — модели таблиц (в том числе для произведения миграций при первом подключении к БД)
		- `functions.py` — функции, предназначенные для получения и управления данными
	- `external/` — скрипты для взаимодействия с внешними API...
		- `foursquare.py` — Foursquare
        - `openstreetmap.py` — OpenStreetMap (Nominatim)
        - `openweathermap.py` — OpenWeatherMap
    - `handlers/` — обработчики запросов, поступающих к боту
      - `имя_папки/` — обработчики разделены на папки (`main_menu`, `user_info`, `travel`, `travel_notes` и `locations`) и файлы (`messages.py`, `callback.py` и `inline.py`) по типам запросов для удобства чтения и работы с кодом
          - `messages.py` — обработка входящих сообщений
          - `callback.py` — обработка нажатий на inline-кнопки
          - `inline.py` — обработка запросов в [inline-режиме](https://core.telegram.org/bots/inline)
    - `keyboards/keyboards.py` C клавиатуры для размещения под сообщениями бота
    - `localization/localization.py` — получение строк по псевдонимам


## Локальный запуск
### Клонирование репозитория
Запустите команду `git clone https://github.com/Central-University-IT-prod/backend-redisner` для клонирования репозитория к себе
### Подготовка
При необходимости измените ключи для API в `.env` файле 
### Запуск
Запустите команду `docker-compose up -d`

# [<img src="https://img.shields.io/badge/Telegram-%40TravelWithIvesBot-blue">](https://t.me/TravelWithIvesBot) [<img src="https://img.shields.io/badge/Заключительный этап-PROD 2024-darkgreen">](https://prodcontest.ru)

# Travel Agent 3.0

## Описание

Telegram бот, предназначенный для помощи в планировании совместных
путешествий

## Как найти бота

Бот доступен по ссылке [@TravelWithIvesBot](https://t.me/TravelWithIvesBot)

Единственный доступный на данный момент язык — русский

## [Как пользоваться ботом](readme/how-to-use.md)

## Используемые технологии

- [aiogram](https://github.com/aiogram/aiogram) — фреймворк для асинхронного взаимодействия с [Telegram Bot API](https://core.telegram.org/bots/api)
- [redis](https://redis.io/) — хранение данных; используется для удобной работы с FSM в aiogram
- [Docker](https://www.docker.com/) и [Docker-Compose](https://docs.docker.com/compose) — быстрый запуск проекта в контейнерах
- [PostgreSQL](https://www.postgresql.org/) — гибкая, многофункциональная и масштабируемая СУБД для управления данными о пользователях, путешествиях и прочими необходимыми для бота данными
- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) — ORM для удобного взаимодействия с СУБД 

## [Схема данных СУБД](readme/database.md)

## Внешние интеграции

- [Foursquare API](https://location.foursquare.com/developer/docs-home) — API с условно-бесплатным доступом, предоставляет простой поиск интересных мест и достопримечательностей по всему миру
- [Nominatim](https://nominatim.openstreetmap.org/ui/about.html) — поисковая система для OpenStreetMap
- [OpenWeatherMap](https://openweathermap.org/api) — API с бесплатным доступом для части запросов, позволяет получить прогноз погоды на ближайшие дни

## Структура проекта

- ### Docker
	- `Dockerfile` — установка Python 3.12 и всех необходимых зависимостей из `requirements.txt`
	- `docker-compose.yml` (список сервисов):
		- `postgres` — инициализация СУБД PostgreSQL 14.5 с пустой базой данных
		- `redis` — инициализация СУБД Redis
		- `bot` — запуск скрипта `__main__.py` в корневой папке проекта
- ### Вспомогательные файлы
	- `.env` — хранение переменных окружения, таких как API токены для Telegram и внешних интеграций
	- `requirements.txt` — список зависимостей для установки при запуске `Dockerfile`
    - `localization/` — локализация бота
      - `locales/**.yaml` — структурированный файл со связями вида `псевдоним_строки: строка`
- ### Python
	- `__main__.py` — основной скрипт, запускающий бота
	- `config.py` — управление переменными окружения
	- `assistive/` — вспомогательные скрипты
		- `callback.py` — объекты `CallbackData` для передачи в inline-кнопки под сообщениями бота
		- `states.py` — объекты `StatesGroup` для работы с FSM и хранения состояний пользователей
		- `processors.py` — функции-обработчики, позволяющие преобразовать "сырые" объекты в тексты и клавиатуры для сообщений
	- `database/` — скрипты, относящиеся к хранению и управлению данными
		- `models.py` — модели таблиц (в том числе для произведения миграций при первом подключении к БД)
		- `functions.py` — функции, предназначенные для получения и управления данными
	- `external/` — скрипты для взаимодействия с внешними API...
		- `foursquare.py` — Foursquare
        - `openstreetmap.py` — OpenStreetMap (Nominatim)
        - `openweathermap.py` — OpenWeatherMap
    - `handlers/` — обработчики запросов, поступающих к боту
      - `имя_папки/` — обработчики разделены на папки (`main_menu`, `user_info`, `travel`, `travel_notes` и `locations`) и файлы (`messages.py`, `callback.py` и `inline.py`) по типам запросов для удобства чтения и работы с кодом
          - `messages.py` — обработка входящих сообщений
          - `callback.py` — обработка нажатий на inline-кнопки
          - `inline.py` — обработка запросов в [inline-режиме](https://core.telegram.org/bots/inline)
    - `keyboards/keyboards.py` C клавиатуры для размещения под сообщениями бота
    - `localization/localization.py` — получение строк по псевдонимам


## Локальный запуск
### Клонирование репозитория
Запустите команду `git clone https://github.com/Central-University-IT-prod/backend-redisner` для клонирования репозитория к себе
### Подготовка
При необходимости измените ключи для API в `.env` файле 
### Запуск
Запустите команду `docker-compose up -d`

