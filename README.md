# bdsm_promo
Бот помошник для работы с промоутерами для VAinc.

Перед стартом необходимо создать виртуальное окружение .venv и установить необходимые библиотеки
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Использует MYSQL базу, поэтому требует для доступа к базе запущенный MYSQL сервер
`systemctl start mariadb.service` или `systemctl enable --now mariadb.service` для включения сервера на старте ПК

Временно в качестве информации о пользователях используется файл `data/users.json`

пример пользователя (поле `rights` берется из файла `utils/users.py`)
```json

  {
    "telegram_id": {
      "username": "telegram_username", 
      "rights": ["GET_MAP"],
      "city": ["Москва"],
      "post": "директор",
      "name": "name surname"
    }
  }
```

При запуске читает переменные окружения из файла `.env`
```bash
BOT_TOKEN=123:QWERTY
USERS_DB_FILE=data/users.json
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=sql_base
```
