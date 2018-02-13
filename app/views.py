from app import app
from flask import render_template, redirect, url_for
from flask_login import current_user, login_user


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
@app.route('/authorize')
def authorize():
    if not current_user.is_is_anonymous:
        return render_template('index.html')
    


# "My problems" page
@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/settings')
def settings():
    return render_template('settings.html')