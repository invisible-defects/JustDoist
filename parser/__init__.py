from .doist import has_preferred_tasks, does_use_regullary

def get_combined_problems(api):
    problems = dict()

    problems[2] = has_preferred_tasks(api)
    problems[3] = does_use_regullary(api)