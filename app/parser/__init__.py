from .problems import *


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
    stats_for_linear_graph_completed = sum(map(lambda x: x['total_completed'], statistics["days_items"]))
    
    return {"graph": stats_for_graph}