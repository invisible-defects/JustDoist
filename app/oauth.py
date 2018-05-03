import abc
import json
from justdoist.settings import OAUTH_CREDENTIALS
from rauth import OAuth2Service


class OAuthSignIn(object, metaclass=abc.ABCMeta):
    providers = None

    def __init__(self, provider_name, client_id, client_secret):
        self.provider_name = provider_name
        self.client_id = client_id
        self.client_secret = client_secret

    @abc.abstractmethod
    def authorize(self):
        pass

    @abc.abstractmethod
    def callback(self):
        pass

    def get_callback_url(self) -> str:
        """
        Generates callback url
        :return:
        """
        return url_for(
            'oauth_callback',
            provider=self.provider_name,
            _external=True
        )

    @classmethod
    def get_provider(cls, provider_name):
        if cls.providers is None:
            cls.providers = {}
            for provider_class in cls.__subclasses__():
                provider = provider_class()
                cls.providers[provider.provider_name] = provider
        return cls.providers[provider_name]


class TodoistSignIn(OAuthSignIn):

    def __init__(self):
        """
        Encapsulates logic for Todoist OAuth.
        """
        super().__init__(
            'todoist',
            OAUTH_CREDENTIALS['todois']['id'],
            OAUTH_CREDENTIALS['todois']['secret'],
        )

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
            scope='data:read_write',
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
