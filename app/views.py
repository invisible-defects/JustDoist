from app import app, db
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user
from .models import User
from .oauth import OAuthSignIn


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

    return render_template('index.html')


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
@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/settings')
def settings():
    return render_template('settings.html')
