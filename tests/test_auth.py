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

    def test_register(self):
        payload = {
            'username': 'Kachulio',
            'email': 'Kachulio@ymail.com',
            'password': '12jkl23@'
        }

        r = self.client.post('/auth/register', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(r.status_code, 201)

    def test_register_with_existing_username(self):
        payload = {
            'username': 'Kachulio',
            'email': 'yahoo@ymail.com',
            'password': '12jkl23@'
        }
        r = self.client.post('/auth/register', data=json.dumps(payload), content_type='application/json')
        payload = {
            'username': 'Kachulio',
            'email': 'yahoo@ymail.com',
            'password': '12jkl23@'
        }
        r = self.client.post('/auth/register', data=json.dumps(payload), content_type='application/json')
        self.assertIn('Username has already been taken', json.loads(r.data.decode())['msg'])

    def test_register_with_existing_email(self):
        payload = {
            'username': 'Kachulio',
            'email': 'yahoo@ymail.com',
            'password': '12jkl23@'
        }
        r = self.client.post('/auth/register', data=json.dumps(payload), content_type='application/json')

        payload = {
            'username': 'David',
            'email': 'yahoo@ymail.com',
            'password': '12jkl23@'
        }
        # make a post with an email that has already been registered with another user
        r = self.client.post('/auth/register', data=json.dumps(payload), content_type='application/json')
        self.assertIn('The email address you have entered is already registered', json.loads(r.data.decode())['msg'])

    def test_user_created_message(self):
        payload = {
            'username': 'Kachulio',
            'email': 'Kachulio@ymail.com',
            'password': '12jkl23@'
        }
        r = self.client.post('/auth/register', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(json.loads(r.data.decode())['msg'], 'user created')