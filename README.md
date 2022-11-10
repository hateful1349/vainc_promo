# bdsm_promo

Бот помошник для работы с промоутерами для VAinc.

Перед стартом необходимо создать виртуальное окружение .venv и установить необходимые библиотеки

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Использует PostgreSQL базу, поэтому требует для доступа к базе запущенный PostgreSQL сервер
`systemctl start postgresql.service` или `systemctl enable postgresql.service` для включения сервера на старте ПК

При запуске читает переменные окружения из файла `.env` (пример можно найти в [defaults/config](defaults/config))

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
! в настоящее время setup.py не вносит в базу записи о всех возможных правах, поэтому будет вызывать ошибку !

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

## TODO

- [ ] Ошибка создания первого пользователя (не пишутся права)
- [ ] Получение карты города
    - [X] Выбор города, если в базе задано больше одного
    - [X] Выбор карты текстовым запросом (при выбранном городе) (сразу пачка карт)
    - [X] Выбор карты через инлайн-кнопочное меню
    - [ ] Выбор карты через aiogram-dialog или реализованное самостоятельно меню с пролистыванием пунктов
    - [X] Выделение главного стилями шрифта (жирный)
    - [X] Быстрое переключение в режим поиска карт
- [X] Получение карты по адресу
    - [X] Выдача карты сразу при точном совпадении адреса
    - [X] Выбор карты по частично совпадающему адресу
    - [X] Быстрое переключение в режим поиска адреса
- [ ] Редактирование прав пользователей
    - [X] Добавление/удаление городов
    - [X] Добавление/удаление прав
    - [X] Редактирование данных
    - [X] Управление начальством
    - [X] Переключение суперпользователя
    - [X] Удаление пользователя
    - [ ] Пролистывание меню пользователей, если их слишком много (aiogram-dialog или собственное)
    - [ ] Toggle кнопки, а не в отдельных группах вида добавить-убрать
    - [ ] Быстрое переключение на меню пользователей
- [ ] Конструктор городов
    - [X] Создание нового города
    - [X] Удаление города
    - [ ] Обновление данных города
    - [ ] Быстрое переключение на конструктор городов
- [ ] Ассинхронная база данных
- [ ] Глобальный реформат
    - [ ] Оформить клавиатуры ввиде отдельных функций/структур
    - [ ] Датакласс с текстом сообщений/кнопок и тп
    - [ ] Переработать систему прав
        - [ ] Роли пользователей, для быстрого назначения прав
        
