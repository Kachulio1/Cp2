import os
basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    """Parent configuration class."""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = 'its not a secret'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

class DevelopmentConfig(Config):
    """Configurations for Development."""
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/bucket'
class TestingConfig(Config):
    """Configurations for Testing, with a separate test database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.sqlite')
    DEBUG = True



app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,

}