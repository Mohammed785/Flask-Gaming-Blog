from rauth import OAuth2Service
from flask import json, url_for,redirect,current_app,request



class OAuthSignIn:
    providers = None
    def __init__(self,provider_name):
        self.provider_name =provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id =credentials['id']
        self.consumer_secert = credentials['secret']
    

    def authorize(self):
        pass

    def callback(self):
        pass

    
    def get_callback_url(self):
        return url_for('auth.oauth_callback',provider=self.provider_name,_external=True)
    
    # used to lookup the correct OAuthSignIn instance
    @classmethod
    def get_provider(self,provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]

# facebook uses OAuth2Service protocol unlike twitter that uses OAuth1Service
class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super(FacebookSignIn,self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secert,
            authorize_url='https://graph.facebook.com/oauth/authorize',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/'
        )
        # the authorize_url and access_token_url are URLs defined by facebook
        # for the app to connect to during the authentication process
        # finally base_url sets the prefix url for facebook api calls once the authentication is complete

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',  # scope arg asks facebook to provide the user's email
            response_type ='code',# response_type tells the OAuth that the application is web application
            redirect_uri = self.get_callback_url()
            # redirect_uri  sets the application route that the provider needs to invoke
            # after it completes the authentication process
        ))

    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))
        
        if 'code' not in request.args:
            return None,None,None
        
        oauth_session = self.service.get_auth_session(
            data = {
                'code':request.arts['code'],
                'grant_type':'authorization_code',
                'redirect_uri':self.get_callback_url()
            },
            decoder = decode_json
        )

        me = oauth_session.get('me?fields=id,email').json()
        return ('facebook$'+me['id'],
                me.get('email').split('@')[0],# facebook does not provide username so use email's user
                me.get('email')
        )