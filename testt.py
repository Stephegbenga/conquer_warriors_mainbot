from controllers.database import Users

users = Users.find({})

for user in users:
    print(user)