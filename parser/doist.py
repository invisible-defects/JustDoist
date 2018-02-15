import todoist


def has_preferred_tasks(mail, password):
    api = todoist.TodoistAPI()
    api.user.login(mail, password)

    return int(max([item["priority"] for item in api.sync()["items"]]) != 1)
