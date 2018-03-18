from app import db
from app.models import User, ProblemProbability

User.query.delete()
ProblemProbability.query.delete()

db.session.flush()
db.session.commit()