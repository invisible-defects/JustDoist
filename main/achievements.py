from todoist import TodoistAPI
from django.core.exceptions import ObjectDoesNotExist


def detect_achievements(user: "JustdoistUser") -> list:
    achievements = set()

    token = user.todoist_token
    # api = TodoistAPI(token)
    try:
        n_completed_steps = user.suggested_problems.all().first().steps_completed
    except ObjectDoesNotExist:
        return []

    n_added_tasks = len(user.suggested_problems.all())

    # task adding related achievements
    if n_added_tasks >= 25:
        achievements |= {0, 1, 2, 3}
    elif n_added_tasks >= 10:
        achievements |= {0, 1, 2}
    elif n_added_tasks >= 5:
        achievements |= {0, 1}
    elif n_added_tasks >= 1:
        achievements |= {0}

    # step solving related achievements
    if n_completed_steps >= 25:
        achievements |= {4, 5, 6 , 7}
    elif n_completed_steps >= 10:
        achievements |= {4, 5, 6}
    elif n_completed_steps >= 5:
        achievements |= {4, 5}
    elif n_completed_steps >= 1:
        achievements |= {4}

    if not user.shown_first_task_ac:
        user.shown_first_task_ac = True
        user.save()
        achievements |= {0}

    return list(achievements)
