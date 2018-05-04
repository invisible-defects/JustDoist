from .problems import *
from .data import *


def get_combined_problems(api):
    problems_dict = dict()
    is_premium(api)
    problems_dict[2] = has_preferred_tasks(api)
    problems_dict[3] = does_use_regularly(api)
    get_stats(api)


    return problems_dict

def get_stats(api):
    statistics = api.completed.get_stats()
    stats_for_graph = statistics["karma_graph_data"]
    if(stats_for_graph[-1]["karma_avg"] < stats_for_graph[0]["karma_avg"]):
        stats_linear_graph = int(int(stats_for_graph[-1]["karma_avg"])/int(stats_for_graph[0]["karma_avg"])*100) * (-1)
    else:
        stats_linear_graph = int(int(stats_for_graph[0]["karma_avg"]) / int(stats_for_graph[-1]["karma_avg"]) * 100)

    stats_for_linear_graph_completed = sum(map(lambda x: x['total_completed'], statistics["days_items"]))
    stats_for_graph_optimized = []
    for i in stats_for_graph:
        stats_for_graph_optimized.append(i["karma_avg"])
    return {"graph": stats_for_graph_optimized, "percentage": stats_linear_graph}

def get_info(api):
    return user_info(api)
