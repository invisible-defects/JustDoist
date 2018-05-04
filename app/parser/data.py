def user_info(api):
    return {"name": api.user.get()["full_name"].title(), "img": api.user.get()["avatar_big"], "email": api.user.get()["email"]}