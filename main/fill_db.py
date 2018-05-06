import json
from load_django import load_django; load_django()
from main.models import SuggestedProblem, ProblemStep


if __name__ == "__main__":
    with open('fill_db_data.json', 'r') as f:
        problems = json.loads(f.read())

    for problem in problems:
        if not SuggestedProblem.objects.filter(uid=problem['uid']):
            continue
        suggestion = SuggestedProblem(
            uid = problem['uid'],
            title = problem['title'],
            body = '\n'.join(problem['body']),
            steps_num = problem['steps_num']
        )
        suggestion.save()
        for step_data in problem['steps']:
            step = ProblemStep(
                related_problem = suggestion,
                number = step_data['number'],
                description = step_data['description'],
                task = step_data['task']
            )
            step.save()
    print("[INFO] SUCCESSFULLY CREATED PRESET PROBLEMS")
