from .problems import has_preferred_tasks, does_use_regularly


def get_combined_problems(api):
    problems_dict = dict()
    problems_dict[2] = has_preferred_tasks(api)
    problems_dict[3] = does_use_regularly(api)

    return problems_dict
