from main.models import ProblemStep, JustdoistUser
from todoist import TodoistAPI


def detecet_achievements(user: JustdoistUser) -> set:
    achievements = set()

    token = user.todoist_token
    api = TodoistAPI(token)
    
    n_completed_steps = len(user.steps_completed.all())
    n_added_tasks = len(api.items.all())

    # task adding related achievements
    if n_added_tasks >= 25:
        achievements |= {0, 1, 2, 3}
    elif n_added_tasks >= 10:
        achievements |= {0, 1, 2}
    elif n_added_tasks >= 5:
        achievements |= {0, 1}
    elif n_added_tasks >= 1:
        achievements |= {0}

    # step solvin related achievements
    if n_completed_steps >= 25:
        achievements |= {4, 5, 6 , 7}
    elif n_completed_steps >= 10:
        achievements |= {4, 5, 6}
    elif n_completed_steps >= 5:
        achievements |= {4, 5}
    elif n_completed_steps >= 1:
        achievements |= {4}
        
    return achievements
