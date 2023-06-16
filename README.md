# VAinc_promo `0.3.9`

Данный проект создан для того, чтобы помочь менеджерам VAinc при работе с промоутерами.

> :warning: **Не стабильная версия**: Проект пока в разработке, поэтому тяжело выделить стабильный релиз. Рекомендуется использовать [e1005b](https://github.com/viktory683/vainc_promo/commit/e1005b676bc088efbef6fd4caf6af956cf5407e3). [Понизить версию](#понизить-версию-до-e1005b6)

## Возможности

- Получить карту по имени/адресу
- Конструктор городов
    - Создание
        - Парсер таблицы с адресами и архива с картами
    - Обновление [TODO](#todo)
    - Удаление
- Управление пользователями
    - Добавить/изменить/удалить пользователя
    - Добавить/изменить/удалить группу [TODO](#todo)
    - Назначить права пользователю/группе
        - Права пользования возможностями бота
        - Права обращения к ресурсам бота (городу и тп)

## Оглавление

- [Установка](#установка)
    - [Из исходников](#из-исходников)
    - [Docker](#docker)
- [Обновление](#обновление)
- [TODO](#todo)
- [Проблемы](#проблемы)

## Установка

### Из исходников

```bash
$ git clone https://github.com/viktory683/vainc_promo.git
```

Перед стартом необходимо создать виртуальное окружение .venv и установить необходимые библиотеки

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> :warning: **Устаревшие версии библиотек**: При обновления питона до более новой версии некоторые зависимости могут быть поломаны. См. [Проблемы](#обновленный-питон)

Для хранения данных используется PostgreSQL, поэтому требуется запущенный PostgreSQL сервер
```bash
# systemctl start postgresql.service
```
или
```bash
# systemctl enable postgresql.service
```
для включения СУБД при старте сервера

При запуске бот читает переменные окружения из файла `.env` (пример можно найти в [defaults/config](defaults/config))

Его необходимо создать вручную
```bash
$ touch .env
```

Затем прописать все необходимые переменные

```bash
BOT_TOKEN=000000000:00000000000000000000000000000000000

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=sql_base

DB_TYPE=psql

LOGLEVEL=info

ADDRESS_SEARCH_COUNT=5
```

Перед стартом необходимо запустить [скрипт настройки нулевого пользователя](setup.py) для создания нужных записей в базе

```bash
python -m venv .venv
source .venv/bin/activate
python setup.py
```

Запуск: передать `python` на исполнение [main.py](main.py) (из под виртуального окружения `source .venv/bin/activate`
см. выше)

```bash
python main.py
```

### Docker

```
todo
```

## Обновление

```
todo
```

## TODO

- [ ] Карты
    - [ ] Выбор карты через aiogram-dialog или реализованное самостоятельно меню с пролистыванием  пунктов
    - [ ] Переписать поиск подходящего адреса, используя SequenceMatcher
        - [ ] Совместить поиск адреса с поиском по имени карты используя фильтропоиск
        - [ ] Переписать фильтропоиск на Rust/C/C++ с FFI (вероятно он будет слишком медленный на Python)
- [ ] Редактирование прав пользователей
    - [ ] Пролистывание меню пользователей, если их слишком много (aiogram-dialog или собственное)
    - [ ] Toggle кнопки, а не в отдельных группах вида добавить-убрать (aiogram-dialog или собственное)
    - [ ] Убрать возможность у суперпользователя забирать у себя права суперпользователя
- [ ] Конструктор городов
    - [ ] Обновление данных города
- [ ] Ассинхронная база данных
- [ ] Глобальный рефактор
    - [ ] Оформить клавиатуры ввиде отдельных функций/структур
    - [ ] Датакласс/JSON с текстом сообщений/кнопок и тп
    - [ ] Переработать систему прав (Unix-подобная)
        ```
        Добавляется новая сущность: ресурс (вероятно будет переименованно).
        Ресурс представляет собой те или иные данные (Город - ресурс)
        Пользователь может владеть ресурсом, соответственно имея к нему полный доступ.
        Пользователя можно добавить в группу, которой можно дать права на использование ресурса.
        ```
    - [ ] Рефактор хендеров для быстрого переключения (на данный момент сделано через костыли)
    - [ ] Переписать алхимию на версию 2.x.x
    - [ ] Alembic для контроля версии схемы базы
- [ ] Скрипт полуавтоматической установки
    - [ ] Создание виртуального окружения
    - [ ] Установка необходимых зависимостей
    - [ ] Форма ввода необходимых параметров (включая ID рут пользователя)
    - [ ] Создание и включение systemctl-сервиса для управления работы бота
        
## Проблемы

### Обновленный питон

Перед установкой необходимых зависимостей (`pip install -r requirements.txt`) может помочь замена всех `==` на `>=`.

Пример:
- Старый `requirements.txt`
    ```
    ...
    aiogram==2.25.1
    aiohttp==3.8.4
    ...
    ```
- Новый `requirements.txt`
    ```
    ...
    aiogram>=2.25.1
    aiohttp>=3.8.4
    ...
    ```


### Понизить версию до e1005b6

```bash
git reset --hard e1005b6
```