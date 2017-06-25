import json
from flask_testing import TestCase
from app import create_app, db
from config import app_config


class TestAuth(TestCase):
    def create_app(self):
        app = self.app = create_app(app_config['testing'])
        return app

    def setUp(self):
        # create a client for making posts
        self.client = self.create_app().test_client()

        # This will create the database file using SQLAlchemy
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def register_user(self):
        payload = {
            'username': 'Monica',
            'email': 'wahu@waru.com',
            'password': 'me'
        }
        self.client.post('/auth/register', data=json.dumps(payload), content_type='application/json')

    def login_user(self):
        payload = {
            'username': 'Monica',
            'password': 'me'
        }
        r = self.client.post('/auth/login', data=json.dumps(payload), content_type='application/json')
        return json.loads(r.data.decode())['access_token']

    def test_bucketlist_creation(self):
        """Test API can create a bucketlist (POST request)"""
        self.register_user()
        access_token = self.login_user()
        body = {
            'name': 'Go to mombasa'
        }
        # create a bucketlist by making a POST request
        r = self.client.post(
            '/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=body)
        self.assertEqual(r.status_code, 201)
        self.assertIn('Go to mombasa', str(r.data))