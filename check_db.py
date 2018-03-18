from app.models import User, Problem, ProblemProbability

users = User.query.all()
problems = Problem.query.all()
probs = ProblemProbability.query.all()

print(users)
print(problems)
print(probs)