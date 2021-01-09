def addUser(bot, dm, conv_id, user_id):
    user = bot.get_chat_member(conv_id, user_id).user
    l = [
        user.id,
        user.first_name,
        user.last_name,
        user.username,
        user.first_name,
        user.last_name,
    ]
    #','.join([str(i) for i in l])
    users = dm.getRessource(conv_id, "users")
    if len(users) > 1:
        users = [i.split(",") for i in users.split("\n")]
    else:
        users = []
    ids = [i[0] for i in users]
    ind = 0
    try:
        ind = ids.index(l[0])
    except:
        ind = -1
    if ind != -1:
        if [user.first_name, user.last_name, user.username] != users[ind][1:4]:
            print("New")
    else:
        dm.saveRessource(conv_id, "users", ",".join([str(i) for i in l]) + "\n", "a")
