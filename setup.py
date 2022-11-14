from database.users import Users

admin_id = input("id главного в боте (можно посмотреть через https://t.me/userinfobot)\n>")

Users.first_user(admin_id)
