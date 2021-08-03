class Config:
    SECRET_KEY = '86cbed706b49dd1750b080f06d030a23'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS =False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

    MAIL_SERVER = 'smtp@google.com'
    MAIL_PASSWORD = ''
    MAIL_USERNAME = ''
    MAIL_PORT = 456
    MAIL_USE_SSL = True

    ELASTICSEARCH_URL = 'http://localhost:9200'

    # OAuth Config
    # you can get the id and secret from the provider and add them here
    # you get them from provider developer site
    OAUTH_CREDENTIALS = {
        'facebook': {
            'id': '',
            'secret': ''
        }
    }
