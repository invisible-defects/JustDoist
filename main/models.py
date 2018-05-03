from datetime import datetime

import todoist
from django.db import models
from django.contrib.auth.models import User
from requests import HTTPError

from main.api_utils import get_stats, get_combined_problems


class JustdoistUser(User):
    possible_problems = [2, 3]

    todoist_token = models.CharField(unique=True, max_length=128, required=False)
    last_problem_shown = models.DateTimeField(null=True)
    inbox_id = models.IntegerField(null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_stats(self) -> dict:
        api = todoist.TodoistAPI(self.todoist_token)
        return get_stats(api)

    def link_todoist(self, api_key: str):
        self.todoist_token = api_key

    def check_todoist(self) -> bool:
        api = todoist.TodoistAPI(self.todoist_token)
        try:
            data = api.sync()
            return "sync_token" in data
        except (HTTPError, ValueError):
            return False

    def _get_highest_probability(self) -> "ProblemProbability":
        return self.suggested_problems.objects.filter(
            is_being_solved=False
        ).order_by('-value').first()

    def get_problem(self) -> dict:
        if self.last_problem_shown is not None:
            delta = datetime.now() - self.last_problem_shown
            if delta.days < 1:
                return {"status": 'time', 'problem': None}

        problem = self._get_highest_probability()
        # TODO: probably need to extract a constant
        if problem is None or problem.value < 0.3:
            self.calculate_probabilities()
            problem = self._get_highest_probability()

        # TODO: change `problem` key because that's actually a probability
        if problem is None or problem.value < 0.3:
            return {"status": "no", "problem": None}

        return {"status": 'ok', "problem": problem}

    def calculate_probabilities(self) -> bool:
        if not self.check_todoist():
            return False

        api = todoist.TodoistAPI(self.todoist_token)
        data = get_combined_problems(api)
        for problem in self.possible_problems:
            value = data[problem]
            proba = self.suggested_problems.object.get(suggest_problem=problem).first()
            if proba is None:
                proba = ProblemProbability(
                    value=value,
                    suggested_problem=problem,
                    user=self
                )
                proba.save()

        return True

    def get_inbox_id(self, api):
        if self.inbox_id is not None:
            return self.inbox_id
        for project in api.state['projects']:
            if project['inbox_project']:
                return project['id']

    def add_problem(self, text: str, problem_id: int) -> bool:
        if not self.check_todoist():
            return False
        proba = self.suggested_problems.objects.filter_by(problem_id).first()
        proba.steps_completed += 1
        proba.save()
        api = todoist.TodoistAPI(self.todoist_token)
        api.items.add(text, self.get_inbox_id(api))
        api.commit()
        return True


class Problem(models.Model):
    user = models.ForeignKey(JustdoistUser, on_delete=models.CASCADE, related_name="problems")
    title = models.CharField(max_length=128)
    body = models.CharField(max_length=10000)
    steps = models.CharField(max_length=10000)
    steps_num = models.IntegerField(default=1)

    def __str__(self):
        return f"<Problem {self.pk} \"{self.title}\">"


class ProblemProbability(models.Model):
    value = models.FloatField()
    suggested_problem = models.IntegerField()
    user = models.ForeignKey(JustdoistUser, on_delete=models.CASCADE, related_name="suggested_problems")
    steps_completed = models.IntegerField(default=0)
    is_being_solved = models.BooleanField(default=False)

    def __str__(self):
        return (f"<ProblemProbability [{self.problem.pk}] "
                f"{self.value * 100:.2f}%, being solved: {self.is_being_solved}>")
