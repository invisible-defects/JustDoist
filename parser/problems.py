from dateutil import parser


def has_preferred_tasks(api):
    return int(max([item["priority"] for item in api.items.all()]) != 1)


def does_use_regularly(api):
    return int(sum(map(lambda x: x['total_completed'], api.completed.get_stats()['days_items'])) < 7)
