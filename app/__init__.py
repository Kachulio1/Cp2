from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# initialize sql-alchemy
db = SQLAlchemy()
# Setup for the Flask-JWT-Extended extension
jwt = JWTManager()


# function factory to create app with different settings for the current app that's being created
def create_app(config_name):

    # instantiate a WSGI application object
    app = Flask(__name__)
    # and get settings configurations from config.py file
    app.config.from_object(config_name)

    # initialize database object which is imported
    # in models.py and in tests
    db.init_app(app)
    jwt.init_app(app)

    # import auth blueprint and register it to the WSGI app and also buckets
    from app.auth import views
    app.register_blueprint(views.auth)

    from app.buckets import views
    app.register_blueprint(views.bucketlist)



    return app
