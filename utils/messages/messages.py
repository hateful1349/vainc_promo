from dataclasses import dataclass

from specials.singleton import Singleton


@dataclass
class Messages(Singleton):
    default_message_rights = "Все возможные для вас действия можно сделать по кнопкам ниже"
    default_message_null = f"Вы не можете использовать данного бота\n" \
                           f"Если вы считаете, что это ошибка, то обратитесь к вышестоящему лицу за подробностями"

    city_new_city_question = "Как будет зваться новый город?"

    @classmethod
    def city_xlsx_send(cls, city_name) -> str:
        return f"Теперь отправьте мне xlsx-файл с данными по городу {city_name}"

    city_cancel_message = "Если ошиблись, то можете написать /cancel и повторить заново"

    awesome = "Отлично!"

    users_new_user_btn = "➕ Новый юзер"

    @property
    def test(self):
        return "line"
