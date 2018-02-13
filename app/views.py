from app import app, db
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user
from .models import User
from .oauth import OAuthSignIn


# Main (problems) page
@app.route('/')
@app.route('/index')
def index():
    if current_user.is_anonymous:
        return redirect(url_for('login'))

    return render_template('index.html')


# Start login page w button
@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    return render_template('login.html')


# Authorization page
@app.route('/authorize/<provider>')
def authorize(provider):
    if not current_user.is_is_anonymous:
        return render_template('index.html')
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    token, token_type = oauth.callback()
    if token is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(todoist_token=token).first()
    if not user:
        user = User(todoist_token=token)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))


# "My problems" page
@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/settings')
def settings():
    return render_template('settings.html')
