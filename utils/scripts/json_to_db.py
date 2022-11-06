# import sys
#
# from database.base import db_session
# from database.models import User, Right, City
# from database.users import Rights, Users
#
#
# def import_json():
#     """
#     Imports JSON user file to database
#     """
#
#     users_dict = Users.get_users()
#
#     with db_session(mode="w") as session:
#         for right_name in list(Rights.comments.keys()):
#             r = session.query(Right).filter(Right.name.ilike(right_name)).first()
#             if not r:
#                 print(right_name)
#                 session.add(Right(right_name))
#
#     with db_session(mode="w") as session:
#         for user_tg_id, user_values in users_dict.items():
#             user = User(
#                 user_tg_id,
#                 user_values.get("username"),
#                 user_values.get("post"),
#                 user_values.get("name")
#             )
#             for user_right in user_values.get("rights"):
#                 right = session.query(Right).filter(Right.name.ilike(user_right)).first()
#                 user.rights.append(right)
#             for user_city in user_values.get("city"):
#                 city = session.query(City).filter(City.name.ilike(user_city)).first()
#                 if city:
#                     user.cities.append(city)
#             session.add(user)
#
#
# if __name__ == "__main__":
#     import_json()
#
