from app import db, login
import todoist
from flask_login import UserMixin


class User(UserMixin, db.Model):
    todoist_token = db.Column(db.String(128), primary_key=True)
    problems = db.relationship('ProblemProbability', backref='owner', lazy='dynamic')

    def link_todoist(self, api_key):
        self.todoist_token = api_key

    def check_todoist(self):
        api = todoist.TodoistAPI(self.todoist_token)
        if api.sync()['http_code'] == 200:
            return True
        else:
            return False

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Problem(db.Model):
    num = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(10000))
    steps = db.Column(db.String(10000))


class ProblemProbability(db.Model):
    val = db.Column(db.Float)
    problem_num = db.Column(db.Integer, primary_key=True)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))