from todoist import TodoistAPI


def has_preferred_tasks(api: TodoistAPI) -> bool:
    max_prior = max((item['priority'] for item in api.items.all()), default=1)
    return max_prior != 1


def does_use_regularly(api: TodoistAPI) -> float:
    return int(
        sum(map(lambda x: x['total_completed'],
            api.completed.get_stats()['days_items'])) < 7
    )


def is_premium(api: TodoistAPI) -> bool:
    return api.user.get()["is_premium"]


def get_combined_problems(api: TodoistAPI) -> dict:
    # is_premium(api)
    # get_stats(api)
    problems_dict = {}
    problems_dict[2] = has_preferred_tasks(api)
    problems_dict[3] = does_use_regularly(api)
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
    stats_for_graph_optimized = [s.get("kargma_avg", None) for s in stats_for_graph]
    return {"graph": stats_for_graph_optimized, "percentage": stats_linear_graph}
