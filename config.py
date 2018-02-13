import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'just-do-it-dont-let-your-dreams-be-dreams'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OAUTH_CREDENTIALS = {
        'todoist': {
            'id': '30b562cc54f74cd39d46960f68b9b612',
            'secret': '9c218fd301af493497799fc26cb482ac'
        }
    }
