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

    def test_app_is_testing(self):
        """Test the app is using a different database for testing"""
        self.assertTrue(self.app.config['DEBUG'])
        self.assertTrue(
            self.app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:////Users/rey/Desktop/cp2/test.sqlite'

        )

    def test_register(self):
        """Test user registered successfully status code"""
        payload = {
            'username': 'Kachulio',
            'email': 'Kachulio@ymail.com',
            'password': '12jkl23@'
        }

        r = self.client.post('/auth/register', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(201, r.status_code)

    def test_user_created_message(self):
        """Test user registered successfully message"""
        payload = {
            'username': 'addis',
            'email': 'addis@ymail.com',
            'password': 'A155RTD@'
        }
        r = self.client.post('/auth/register', data=json.dumps(payload), content_type='application/json')
        self.assertEqual('User Created', json.loads(r.data.decode())['msg'])

    def test_reject_invalid_characters_in_user_name(self):
        """Test user registering with invalid characters"""
        payload = {
            'username': '*ac$1hul@io',
            'email': 'Kachulio@ymail.com',
            'password': '12jkl23@'
        }

        r = self.client.post('/auth/register', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(400, r.status_code)
        self.assertEqual('Invalid User Name Only Use Alphabet and Numbers', json.loads(r.data.decode())['msg'])

    def test_max_length_username(self):
        """Test user registering with an exceeding maximum characters in the username """
        payload = {
            'username': 'a' * 81,
            'email': 'Kachulio@ymail.com',
            'password': '12jkl23@'
        }

        r = self.client.post('/auth/register', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(400, r.status_code)
        self.assertEqual('Sorry that username is too long (should be no longer than 80 characters)',
                         json.loads(r.data.decode())['msg'])

    def test_empty_username(self):
        """Test user registering without passing a username"""

        payload = {
            'username': '',
            'email': 'Kachulio@ymail.com',
            'password': '12jkl23@'
        }

        r = self.client.post('/auth/register', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(400, r.status_code)
        self.assertEqual('Username is required', json.loads(r.data.decode())['msg'])

    def test_empty_password(self):
        """Test user registering without passing a password"""
        payload = {
            'username': 'linda',
            'email': 'linda@ymail.com',
            'password': ''
        }

        r = self.client.post('/auth/register', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(400, r.status_code)
        self.assertEqual('Please provide a password', json.loads(r.data.decode())['msg'])

    def test_empty_email(self):
        """Test user registering without passing an email"""
        payload = {
            'username': 'hannah',
            'email': '',
            'password': 'peace'
        }

        r = self.client.post('/auth/register', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(400, r.status_code)
        self.assertEqual('Please provide an email', json.loads(r.data.decode())['msg'])

    def test_register_with_existing_username(self):
        """Test when user tries to register with an existing username"""
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
        """Test user registering with a registered email"""
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

    def test_user_login(self):
        """Test registered user can login."""
        payload = {
            'username': 'Kachulio',
            'email': 'Kachulio@ymail.com',
            'password': '12jkl23@'
        }

        r = self.client.post('/auth/register', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(r.status_code, 201)
        # get a login response
        r = self.client.post('/auth/login', data=json.dumps(payload), content_type='application/json')

        # get the results in json format
        result = json.loads(r.data.decode())
        # Test that the response contains success message
        self.assertEqual(result['msg'], "You have logged in successfully.")
        # Assert that the status code is equal to 200
        self.assertEqual(r.status_code, 200)
        self.assertTrue(result['access_token'])

    def test_user_login_with_unregistered_user(self):
        """Test non registered users cannot login."""
        # define a dictionary to represent an unregistered user
        payload = {
            'username': 'Carets',
            'password': 'yes'
        }
        # send a POST request to /auth/login with the data above
        r = self.client.post('/auth/login', data=json.dumps(payload), content_type='application/json')
        # get the result in json
        result = json.loads(r.data.decode())

        # assert that this response must contain an error message
        # and an error status code 401(Unauthorized)
        self.assertEqual(r.status_code, 401)
        self.assertEqual("User name does not exist!", result['msg'])

    def test_user_login_without_username(self):
        """Test user login without setting a username"""
        payload = {
            'username': '',
            'password': '12jkl23@'
        }

        r = self.client.post('/auth/login', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(400, r.status_code)
        self.assertEqual('Username is required', json.loads(r.data.decode())['msg'])

    def test_user_login_without_password(self):
        """Test user login in without setting a password"""
        payload = {
            'username': 'ras',
            'password': ''
        }

        r = self.client.post('/auth/login', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(400, r.status_code)
        self.assertEqual('Password is required', json.loads(r.data.decode())['msg'])

    def test_user_login_with_invalid_password(self):
        """Test user login with a wrong password"""
        payload = {
            'username': 'Kachulio',
            'email': 'Kachulio@ymail.com',
            'password': '12jkl23@'
        }
        self.client.post('/auth/register', data=json.dumps(payload), content_type='application/json')
        # change the password
        payload['password'] = 'not the correct password'

        r = self.client.post('/auth/login', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(401, r.status_code)
        self.assertEqual('Bad  password', json.loads(r.data.decode())['msg'])
