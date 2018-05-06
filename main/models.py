import json
from datetime import datetime, timedelta

import todoist
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AbstractUser
from requests import HTTPError

from main.api_utils import get_stats, get_combined_problems
from justdoist.settings import POSSIBLE_PROBLEMS, PROBLEMS_TO_UID, is_available


# TODO: write comments
class JustdoistUser(AbstractUser):
    todoist_token = models.CharField(unique=True, max_length=128, null=True)
    last_problem_shown = models.DateTimeField(null=True)
    inbox_id = models.IntegerField(null=True)
    avatar = models.CharField(max_length=256, null=True)
    color = models.CharField(max_length=8, default='#e44332ff')

    def get_subscription(self):
        try:
            return self.subscription
        except JustdoistUser.subscription.RelatedObjectDoesNotExist:
            return None

    def unsubscribe(self):
        self.subscription.delete()
        return self

    @property
    def has_avatar(self):
        return self.avatar is not None

    def update_avatar(self):
        if not self.has_todoist_token:
            return
        api = todoist.TodoistAPI(self.todoist_token)
        api.user.sync()
        avatar = api.user.get("avatar_big", None)
        self.avatar = avatar
        return self.has_avatar

    @property
    def has_subscription(self):
        return self.get_subscription() is not None

    @property
    def has_todoist_token(self):
        return self.todoist_token is not None

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

    def _get_highest_probability(self) -> "ProblemProbability":
        return self.suggested_problems.all().filter(
            is_being_solved=False
        ).order_by('-value').first()

    def get_problem(self) -> dict:
        if self.last_problem_shown is not None:
            delta = datetime.now() - self.last_problem_shown.replace(tzinfo=None)
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
        for problem in POSSIBLE_PROBLEMS:
            if not is_available(problem):
                continue
            value = data[problem]
            problem = PROBLEMS_TO_UID[problem]
            proba = self.suggested_problems.all().filter(suggested_problem=problem).first()

            if proba is None:
                sgs_problem = SuggestedProblem.get(problem)
                proba = ProblemProbability(
                    value=value,
                    suggested_problem=sgs_problem,
                    user=self
                )
                proba.save()
                proba.init_tasks()
            else:
                proba.value = value
                proba.save()

        return True

    def get_inbox_id(self, api: todoist.TodoistAPI) -> int:
        if self.inbox_id is not None:
            return self.inbox_id

        for project in api.state['projects']:
            if project['inbox_project']:
                return project['id']

        return -1

    def add_problem(self, text: str, problem_id: int, step_num: int) -> bool:
        if not self.check_todoist():
            return False
        proba = SuggestedProblem.objects.all().filter(uid=problem_id).first().probabilities.filter(user=self).first()
        proba.steps_completed += 1
        proba.save()
        api = todoist.TodoistAPI(self.todoist_token)
        item = api.items.add(text, self.get_inbox_id(api))
        api.commit()
        tracker = SuggestedProblem.objects.all().filter(uid=problem_id).first().steps.filter(number=step_num).first().steps_trackers.filter(related_problem_prob=proba).first()
        tracker.todoist_task_id = item['id']
        tracker.save()
        return True

    def __str__(self):
        return f"<JustdoistUser: {self.username}, premium: {self.has_subscription}>"

    def __repr__(self):
        return str(self)


class SuggestedProblem(models.Model):
    uid = models.IntegerField(primary_key=True, unique=True)
    title = models.CharField(max_length=128)
    body = models.CharField(max_length=10000)
    steps_num = models.IntegerField(default=1)

    @classmethod
    def get(cls, uid: int) -> "SuggestedProblem":
        return cls.objects.get(uid=uid)

    def __str__(self):
        return f"<SuggestedProblem {self.uid} \"{self.title}\">"


class ProblemStep(models.Model):
    related_problem = models.ForeignKey(SuggestedProblem, on_delete=models.CASCADE, related_name="steps")
    number = models.IntegerField(default=-1)
    description = models.CharField(max_length=10000)
    task = models.CharField(max_length=10000)

    def __str__(self):
        return f"<ProblemStep {self.number} \"{self.related_problem.uid}\">"


class ProblemProbability(models.Model):
    value = models.FloatField()
    user = models.ForeignKey(JustdoistUser, on_delete=models.CASCADE, related_name="suggested_problems")
    suggested_problem = models.ForeignKey(SuggestedProblem, on_delete=models.CASCADE, related_name="probabilities")
    steps_completed = models.IntegerField(default=0)
    is_being_solved = models.BooleanField(default=False)

    @property
    def json(self):
        data = []
        for tracker in self.steps_trackers.all():
            step = tracker.step
            data.append({
                "step_id": step.number,
                "step_text": step.description,
                "step_solve": step.task,
                "step_status": tracker.is_completed
            })
        return json.dumps(data)

    def __str__(self):
        return (f"<ProblemProbability [{self.suggested_problem.uid}] "
                f"{self.value * 100:.2f}%, being solved: {self.is_being_solved}>")

    def init_tasks(self):
        for step in self.suggested_problem.steps.all():
            tracker = StepTracker(
                related_problem_prob = self,
                step = step
            )
            tracker.save()


class StepTracker(models.Model):
    related_problem_prob = models.ForeignKey(ProblemProbability, on_delete=models.CASCADE, related_name="steps_trackers")
    step = models.ForeignKey(ProblemStep, on_delete=models.CASCADE, related_name="steps_trackers")
    todoist_task_id = models.CharField(max_length=10000, default='0')

    @property
    def is_completed(self):
        if self.todoist_task_id == '0':
            return 'to_work'
        api = todoist.TodoistAPI(self.related_problem_prob.user.todoist_token)
        item = api.items.get_by_id(self.todoist_task_id)
        if item['item']['checked'] == 0:
            return 'time'
        return 'done'

    def __str__(self):
        return (f"<StepTracker [{self.related_problem_prob.suggested_problem.uid}] "
                f"Step {self.step}, completed: {self.is_completed}>")

      
# TODO: Implement supervisor to disable outdated subscriptions
class PremiumSubscription(models.Model):
    VALUES = {"weekly": 7}
    KINDS = frozenset(VALUES.keys())

    user = models.OneToOneField(JustdoistUser,on_delete=models.CASCADE, related_name="subscription")
    charge_id = models.CharField(max_length=256)
    days = models.IntegerField(default=7)
    end = models.DateField()

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("days", 7)
        kwargs['end'] = datetime.now() + timedelta(days=kwargs['days'])
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"<PremiumSubscription: {(self.end - datetime.now()).days}d, U: {self.user.username}>"

    def __repr__(self):
        return str(self)


class Achievment(models.Model):
    title = models.CharField(max_length=256)
    text = models.CharField(max_length=1000)
    image = models.URLField(max_length=500)
    users = models.ManyToManyField(JustdoistUser, related_name="achievements")
    is_premium = models.BooleanField()

    def __str__(self):
        return f"<Achievement `{self.title}`, Premium: {self.is_premium}>"
      