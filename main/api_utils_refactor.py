import sys; sys.path.append("../")
from config import Config
from main.api_wrapper import get_user_tasks

from todoist.api import TodoistAPI


api_token = "a7ced8b476ac01b1e96ee80fbe185f7bbea4decf"


def uses_task_grouping(api: TodoistAPI) -> bool :
    """Detects if user uses the task grouping feature.
    
    Arguments:
        api {TodoistAPI} -- todoist api
    """

    api.sync()

    return len(api.state["projects"]) > 1


def detect_exhaustion(api: TodoistAPI, threshold:int=6) -> bool:
    """Detects if user assigns too many tasks daily
    
    Arguments:
        api {TodoistAPI} -- todoist api
        threshold {int} -- how many tasks daily are considered too much (default: {6})
    """

    tasks = get_user_tasks(api.token)

    return len([task for task in tasks if task["due"]["date"] == tasks[0]["due"]["date"]]) > threshold


def detect_lack_priorities(api: TodoistAPI) -> bool:
    """Detects if user assigns priorities to their tasks
    
    Arguments:
        api {TodoistAPI} -- todoist api
    """

    return len([task for task in get_user_tasks(api.token) if task["priority"] != 1]) > 0

