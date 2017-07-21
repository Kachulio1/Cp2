import os

from flask_script import Manager # class for handling a set of commands
from flask_migrate import Migrate, MigrateCommand
from app import db, create_app
from config import app_config

app = create_app(app_config[os.environ["APP_SETTINGS"]])
migrate = Migrate(app, db)
manager = Manager(app)


manager.add_command('db', MigrateCommand)

@manager.command
def dropdb():
    db.drop_all()
    print('All tables deleted')

@manager.command
def createdb():
    db.create_all()
    print('All tables created')

if __name__ == '__main__':
    manager.run()