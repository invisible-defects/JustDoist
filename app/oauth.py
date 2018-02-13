from app import app
from flask import url_for, redirect, request
from rauth import OAuth2Service
import json


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = app.config['OAUTH_CREDENTIALS'][provider_name]
        self.client_id = credentials['id']
        self.client_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class TodoistSignIn(OAuthSignIn):
    def __init__(self):
        super(TodoistSignIn, self).__init__('todoist')
        self.service = OAuth2Service(
            name='todoist',
            client_id=self.client_id,
            client_secret=self.client_secret,
            authorize_url='https://todoist.com/oauth/authorize',
            access_token_url='https://todoist.com/oauth/access_token',
            base_url='https://todoist.com/api/v7'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='task:add,data:read',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        if 'code' not in request.args:
            return None, None
        token = self.service.get_access_token(
            data={'client_id': self.client_id,
                  'client_secret': self.client_secret,
                  'code': request.args['code'],
                  'redirect_uri': self.get_callback_url()},
            decoder=decode_json
        )
        return (token)

