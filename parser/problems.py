from dateutil import parser


def has_preferred_tasks(api):
    max_prior = 1
    for item in api.items.all():
        try:
            max_prior = max(int(item['priority']), max_prior)
        except KeyError:
            continue
    return max_prior != 1


def does_use_regularly(api):
    return int(sum(map(lambda x: x['total_completed'], api.completed.get_stats()['days_items'])) < 7)
