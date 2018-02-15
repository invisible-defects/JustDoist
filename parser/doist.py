import todoist
import pprint


def has_preferred_tasks(api):
    return int(max([item["priority"] for item in api.sync()["items"]]) != 1)

def does_use_regullary(api):
    return api.sync()


if __name__ == "__main__":
    api = todoist.TodoistAPI()
    api.user.login("denis.mazur.02@inbox.ru", "Freund2002")

    pprint.pprint(does_use_regullary(api))
