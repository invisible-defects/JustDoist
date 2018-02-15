from app import db, login
import todoist
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    todoist_token = db.Column(db.String(128))
    problems = db.relationship('ProblemProbability', backref='owner', lazy='dynamic')
    last_problem_shown = db.Column(db.DateTime())

    def link_todoist(self, api_key):
        self.todoist_token = api_key

    def check_todoist(self):
        api = todoist.TodoistAPI(self.todoist_token)
        if api.sync()['http_code'] == 200:
            return True
        else:
            return False

    def get_problem(self):
        problems = self.problems.query.filter_by()

    def count_probabilities(self):
        pass

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Problem(db.Model):
    __tablename__ = 'problems'
    num = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(10000))
    steps = db.Column(db.String(10000))
    steps_num = db.Column(db.Integer)


class ProblemProbability(db.Model):
    __tablename__ = 'problem_probability'
    val = db.Column(db.Float)
    problem_num = db.Column(db.Integer)
    user_token = db.Column(db.String(128), db.ForeignKey('users.todoist_token'), primary_key=True)
    steps_completed = db.Column(db.Integer)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))