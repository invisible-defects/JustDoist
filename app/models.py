from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    todoist_token = db.Column(db.String(128))
    problems = db.relationship('ProblemProbability', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Problem(db.Model):
    num = db.Column(db.Integer)
    body = db.Column(db.String(10000))
    steps = db.Column(db.String(10000))


class ProblemProbability(db.Model):
    val = db.Column(db.Float)
    problem_num = db.Column(db.Integer)