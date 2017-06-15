from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_file):
    """Create an application instance"""
    app = Flask(__name__)
    
    # back to this soon
    app.config.from_pyfile(config_file)

    # initialize the db instance of SQAlchemy
    db.init(app)
