import os
import unittest
from flask_script import Manager # class for handling a set of commands
from flask_migrate import Migrate, MigrateCommand
from app import db, create_app
from config import app_config

app = create_app(app_config['development'])
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
