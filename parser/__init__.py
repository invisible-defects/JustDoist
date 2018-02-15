from .doist import has_preferred_tasks

def get_combined_problems(api):
    problems = dict()

    problems[2] = has_preferred_tasks(api)