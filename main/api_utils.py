from todoist.api import TodoistAPI


def has_preferred_tasks(api: TodoistAPI) -> bool:
    max_prior = max((item.data.get("priority", -1000) for item in api.items.all()), default=1)
    return max_prior == 1

  
def does_use_regularly(api: TodoistAPI) -> float:
    return int(
        sum(map(lambda x: x['total_completed'],
            api.completed.get_stats()['days_items'])) < 7
    )

  
def uses_task_grouping(api: TodoistAPI) -> bool :
    """Detects if user uses the task grouping feature.
    
    Arguments:
        api {TodoistAPI} -- todoist api
    """

    api.sync()

    return len(api.state["projects"]) > 1


def detect_exhaustion(api: TodoistAPI, threshold=6) -> bool:
    """Detects if user assigns too many tasks daily
    
    Arguments:
        api {TodoistAPI} -- todoist api
        threshold {int} -- how many tasks daily are considered too much (default: {6})
    """

    tasks = api.items.all()
    return len([task["date_string"] for task in tasks if task == tasks[0]["date_string"]]) > threshold



def detect_lack_priorities(api: TodoistAPI) -> bool:
    """Detects if user assigns priorities to their tasks
    
    Arguments:
        api {TodoistAPI} -- todoist api
    """

    return len([task for task in get_user_tasks(api.token) if task["priority"] != 1]) > 0

def detect_regular_use(api: TodoistAPI) -> bool:
    """Detect if user uses Todoist regularly
    
    Arguments:
        api {TodoistAPI} -- todoist api
    """

    return sum(map(lambda x: x['total_completed'],
        api.completed.get_stats()['days_items'])) < 7


def get_combined_problems(api: TodoistAPI) -> dict:
    # is_premium(api)
    # get_stats(api)
    problems_dict = {}

    problems_dict["task_grouping"] = uses_task_grouping(api)
    problems_dict["exhaustion"] = detect_exhaustion(api)
    problems_dict["lack_priorities"] = detect_lack_priorities(api)
    problems_dict["regular_use"] = detect_regular_use(api)

    return problems_dict


def get_stats(api: TodoistAPI) -> dict:
    statistics = api.completed.get_stats()
    stats_for_graph = statistics["karma_graph_data"]

    # TODO: describe this shit
    if (stats_for_graph[-1]["karma_avg"] < stats_for_graph[0]["karma_avg"]):
        stats_linear_graph = -int(
            int(stats_for_graph[-1]["karma_avg"]) /
            int(stats_for_graph[0]["karma_avg"]) * 100
        )
    else:
        stats_linear_graph = int(
            int(stats_for_graph[0]["karma_avg"]) /
            int(stats_for_graph[-1]["karma_avg"]) * 100
        )

    # stats_for_linear_graph_completed = sum(map(lambda x: x['total_completed'], statistics["days_items"]))
    stats_for_graph_optimized = [s.get("karma_avg", None) for s in stats_for_graph]
    return {"graph": stats_for_graph_optimized, "percentage": stats_linear_graph}
