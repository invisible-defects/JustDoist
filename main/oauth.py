import abc
import json

from rauth import OAuth2Service
from django.contrib.sites.shortcuts import get_current_site

from justdoist.settings import OAUTH_CREDENTIALS


class OAuthSignIn(object, metaclass=abc.ABCMeta):
    providers = None

    def __init__(self, provider_name, client_id, client_secret):
        self.provider_name = provider_name
        self.client_id = client_id
        self.client_secret = client_secret

    @abc.abstractmethod
    def authorize(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def callback(self, *args, **kwargs):
        pass

    def get_callback_url(self, request) -> str:
        """
        Generates callback url
        :return:
        """
        print(get_current_site(request).domain)
        return f'{get_current_site(request).domain}/oauth_callback/{self.provider_name}/'

    @classmethod
    def get_provider(cls, provider_name, *args, **kwargs):
        if cls.providers is None:
            cls.providers = {}
            for provider_class in cls.__subclasses__():
                provider = provider_class(*args, **kwargs)
                cls.providers[provider.provider_name] = provider
        return cls.providers[provider_name]


class TodoistSignIn(OAuthSignIn):

    def __init__(self):
        """
        Encapsulates logic for Todoist OAuth.
        """
        super().__init__(
            'todoist',
            OAUTH_CREDENTIALS['todoist']['id'],
            OAUTH_CREDENTIALS['todoist']['secret'],
        )

        self.service = OAuth2Service(
            name='todoist',
            client_id=self.client_id,
            client_secret=self.client_secret,
            authorize_url='https://todoist.com/oauth/authorize',
            access_token_url='https://todoist.com/oauth/access_token',
            base_url='https://todoist.com/api/v7'
        )

    def authorize(self, request):
        s = self.service.get_authorize_url(
            scope='data:read_write',
            response_type='code',
            redirect_uri=self.get_callback_url(request)
        )
        print(s)
        return s

    def callback(self, request):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        if 'code' not in request.GET:
            return None, None

        token = self.service.get_access_token(
            data={'client_id': self.client_id,
                  'client_secret': self.client_secret,
                  'code': request.GET['code'],
                  'redirect_uri': self.get_callback_url(request)},
            decoder=decode_json
        )
        return token
