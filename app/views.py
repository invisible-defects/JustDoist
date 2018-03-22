from app import app, db
import datetime
from flask import render_template, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
from .models import User, ProblemProbability, Problem
from .oauth import OAuthSignIn
import json

DEBUG = True


def alert(message):
    if DEBUG:
        print(message)


# Main (problems) page
@app.route('/')
@app.route('/index')
def index():
    if current_user.is_anonymous:
        print('anonymous trying to go index!')
        return redirect(url_for('login'))

    problem_q = current_user.get_problem()
    butt = True

    if problem_q['status'] == 'no':
        problem = "Seems like you have no problems now.\nHooray!\nCome back later."
        butt = False
    elif problem_q['status'] == 'time':
        problem = "Come back tomorrow for more advice!\nYou can work on your current problems now."
        butt = False
    else:
        prob_raw = Problem.query.filter_by(num=problem_q['problem'].problem_num).first()
        problem = prob_raw.body

    return render_template('index.html', problem_text=problem, butt=butt)


# Start login page w button
@app.route('/login')
def login():
    if current_user.is_authenticated:
        alert('REDIRECTING TO INDEX BC NOT ANONYMOUS')
        return redirect(url_for('index'))

    return render_template('login.html')


# Authorization page
@app.route('/authorize/<provider>')
def authorize(provider):
    if not current_user.is_anonymous:
        alert('REDIRECTING TO INDEX BC NOT ANONYMOUS')
        return render_template('index.html')
    alert('STARTED AUTHORIZING')
    oauth = OAuthSignIn.get_provider(provider)
    alert('PROVIDER: {}'.format(provider))
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    alert('STARTING CALLBACK')
    if not current_user.is_anonymous:
        alert('REDIRECTING TO INDEX BC ANONYMOUS')
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    token = oauth.callback()
    if token is None:
        alert('REDIRECTING TO INDEX BC LOGIN FAILED')
        return redirect(url_for('index'))
    alert('TOKEN: {}'.format(token))
    user = User.query.filter_by(todoist_token=token).first()
    if not user:
        user = User(todoist_token=token)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    alert('LOGGED IN!')
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# "My problems" page
@app.route('/profile/<data>')
def profile(data):
    if data == 'add':
        pr = current_user.get_problem()['problem']
        pr.is_being_solved = True
        current_user.last_problem_shown = datetime.datetime.now()
        db.session.add(pr)
        db.session.add(current_user)
        db.session.commit()
    problem_probs = ProblemProbability.query.filter_by(user_token=current_user.todoist_token, is_being_solved=True)
    problems = []
    for prob in problem_probs:
        prob_raw = Problem.query.filter_by(num=prob.problem_num).first()
        problems.append(
            {'title': prob_raw.title,
             'percantage': int(int(prob.steps_completed)/int(prob_raw.steps_num)*100),
             'id': prob.problem_num}
        )
    return render_template('profile.html', probs=problems)


@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/contact_us')
def contact_us():
    return render_template('contact_us.html')


@app.route('/problem')
def problem():
    prid = request.args.get('problem_id')
    return Problem.query.filter_by(num=prid).first().steps.replace("*", "")


@app.route('/add_task')
def add_task():
    task_text = request.args.get('text')
    task_id = request.args.get('id')
    current_user.add_problem(task_text, task_id)
    return "true"

@app.route('/statistics')
def statistics():
    stats = current_user.get_stats()
    return json.dumps(stats)