from app import app
from flask import render_template
import flask_login


@app.route('/')
@app.route('/index')
def index():
    return 'Hello, world!'


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/settings')
def settings():
    return render_template('settings.html')