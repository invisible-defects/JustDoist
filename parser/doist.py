import todoist
from dateutil import parser

from pprint import pprint


def has_preferred_tasks(api):
    return int(max([item["priority"] for item in api.sync()["items"]]) != 1)

def does_use_regullary(api):
    dates = [parser.parse(event["event_date"]) for event in api.activity.get()]

    return int(max([(dates[i] - dates[i+1]).days for i in range(len(dates) - 1)]) < 4)


if __name__ == "__main__":
    api = todoist.TodoistAPI()
    api.user.login("myaddictionisguitars@gmail.com", "BUMbumsasha2018")

    pprint(does_use_regullary(api))
    