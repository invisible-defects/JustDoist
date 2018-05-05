from datetime import datetime, timedelta

import todoist
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AbstractUser
from requests import HTTPError

from main.api_utils import get_stats, get_combined_problems
from main.presets import PredefinedProblems


# TODO: write comments
class JustdoistUser(AbstractUser):
    possible_problems = [2, 3]
    todoist_token = models.CharField(unique=True, max_length=128, null=True)
    last_problem_shown = models.DateTimeField(null=True)
    inbox_id = models.IntegerField(null=True)
    is_premium = models.BooleanField(default=False)
    premium_end = models.DateTimeField(null=True)

    def get_stats(self) -> dict:
        if not self.check_todoist():
            return {}
        api = todoist.TodoistAPI(self.todoist_token)
        return get_stats(api)

    def link_todoist(self, api_key: str):
        self.todoist_token = api_key

    def check_todoist(self) -> bool:
        api = todoist.TodoistAPI(self.todoist_token)
        try:
            data = api.sync()
            return "sync_token" in data
        except (HTTPError, ValueError, TypeError):
            return False

    def get_premium(self, days: int=7):
        self.is_premium = True
        self.premium_end = datetime.now() + timedelta(days=days)

    def _get_highest_probability(self) -> "ProblemProbability":
        return self.suggested_problems.all().filter(
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
            proba = self.suggested_problems.all().filter(suggested_problem=problem).first()

            if proba is None:
                sgs_problem = SuggestedProblem.get(problem)
                proba = ProblemProbability(
                    value=value,
                    suggested_problem=sgs_problem,
                    user=self
                )
                proba.save()

        return True

    def get_inbox_id(self, api: todoist.TodoistAPI) -> int:
        if self.inbox_id is not None:
            return self.inbox_id

        for project in api.state['projects']:
            if project['inbox_project']:
                return project['id']

        return -1

    def add_problem(self, text: str, problem_id: int) -> bool:
        if not self.check_todoist():
            return False
        proba = self.suggested_problems.all().filter(uid=problem_id).first()
        proba.steps_completed += 1
        proba.save()
        api = todoist.TodoistAPI(self.todoist_token)
        api.items.add(text, self.get_inbox_id(api))
        api.commit()
        return True


class SuggestedProblem(models.Model):
    uid = models.IntegerField(primary_key=True, unique=True)
    title = models.CharField(max_length=128)
    body = models.CharField(max_length=10000)
    steps = models.CharField(max_length=10000)
    steps_num = models.IntegerField(default=1)

    @classmethod
    def get(cls, uid: int) -> "SuggestedProblem":
        try:
            return cls.objects.get(uid=uid)
        except ObjectDoesNotExist:
            problem = cls(**PredefinedProblems.get_problem(uid))
            problem.save()
            return problem

    def __str__(self):
        return f"<SuggestedProblem {self.uid} \"{self.title}\">"


class ProblemProbability(models.Model):
    value = models.FloatField()
    user = models.ForeignKey(JustdoistUser, on_delete=models.CASCADE, related_name="suggested_problems")
    suggested_problem = models.ForeignKey(SuggestedProblem, on_delete=models.CASCADE, related_name="probabilities")
    steps_completed = models.IntegerField(default=0)
    is_being_solved = models.BooleanField(default=False)

    def __str__(self):
        return (f"<ProblemProbability [{self.suggested_problem.uid}] "
                f"{self.value * 100:.2f}%, being solved: {self.is_being_solved}>")
