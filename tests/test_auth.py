import json
from flask_testing import TestCase
from app import create_app, db
from config import app_config

class TestAuth(TestCase):
    def create_app(self):
        app = self.app = create_app(app_config['testing'])
        return app

    def setUp(self):
        self.client = self.create_app().test_client()
        db.create_all()