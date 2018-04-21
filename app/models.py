import datetime

import todoist
from flask_login import UserMixin

from app import db, login, parser

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    todoist_token = db.Column(db.String(128))
    problems = db.relationship('ProblemProbability', backref='owner', lazy='dynamic')
    last_problem_shown = db.Column(db.DateTime())
    inbox_id = None

    possible_problems = [2, 3]

    def get_stats(self):
        api = todoist.TodoistAPI(self.todoist_token)
        return parser.get_stats(api)

    def link_todoist(self, api_key):
        self.todoist_token = api_key

    def check_todoist(self):
        api = todoist.TodoistAPI(self.todoist_token)
        try:
            data = api.sync()
        except Exception as e:
            return False
        if 'sync_token' in data:
            return True
        else:
            return False

    def get_problem(self):
        if self.last_problem_shown is not None:
            delta = datetime.datetime.now() - self.last_problem_shown
            if delta.days < 1:
                return {'status': 'time', 'problem': None}

        problem = ProblemProbability.query.filter_by(
            user_token=self.todoist_token).filter_by(is_being_solved=False).order_by(
            ProblemProbability.val.desc()).first()

        if problem is None or problem.val < 0.3:
            self.count_probabilities()
            problem = ProblemProbability.query.filter_by(
                user_token=self.todoist_token).filter_by(is_being_solved=False).order_by(
                ProblemProbability.val.desc()).first()


        if problem is None:
            return {'status': 'no', 'problem': None}
        if problem.val < 0.3:
            return {'status': 'no', 'problem': None}
        return {'status': 'ok','problem':problem}

    def count_probabilities(self):
        if not self.check_todoist():
            return False
        api = todoist.TodoistAPI(self.todoist_token)
        data = parser.get_combined_problems(api)
        for problem in self.possible_problems:
            val = data[problem]
            prob = ProblemProbability.query.filter_by(problem_num=problem).first()
            if prob is None:
                prob = ProblemProbability(val=val, problem_num=problem, user_token=self.todoist_token,
                                          steps_completed=0)
            db.session.add(prob)
            db.session.commit()

    def get_inbox_id(self, api):
        if self.inbox_id is not None:
            return self.inbox_id
        for project in api.state['projects']:
            if project['inbox_project']:
                return project['id']

    def add_problem(self, text, pr_id):
        if not self.check_todoist():
            return False
        
        prob = ProblemProbability.query.filter_by(user_token=self.todoist_token).filter_by(problem_num=pr_id).first()
        prob.steps_completed += 1
        db.session.add(prob)
        db.session.commit()
        api = todoist.TodoistAPI(self.todoist_token)
        item = api.items.add(text, self.get_inbox_id(api))
        api.commit()

    def __repr__(self):
        return '<User {} {}>'.format(self.id, self.todoist_token)


class Problem(db.Model):
    __tablename__ = 'problems'
    num = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(10000))
    steps = db.Column(db.String(10000))
    steps_num = db.Column(db.Integer)

    def __repr__(self):
        return '<Problem {} "{}">'.format(self.num, self.title)


class ProblemProbability(db.Model):
    __tablename__ = 'problem_probability'
    id = db.Column(db.Integer, primary_key=True)
    val = db.Column(db.Float)
    problem_num = db.Column(db.Integer)
    user_token = db.Column(db.String(128), db.ForeignKey('users.todoist_token'))
    steps_completed = db.Column(db.Integer)
    is_being_solved = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<ProblemProbability {} {}%>'.format(self.problem_num, self.val*100)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
