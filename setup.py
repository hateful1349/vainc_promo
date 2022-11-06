from database.users import Users, Rights

admin_id = input("id главного в боте (можно посмотреть через https://t.me/userinfobot)\n>")

Users.new_user(admin_id)
Users.toggle_super(admin_id)
Users.add_right(admin_id, Rights.CHANGE_USER_PERMISSIONS)
