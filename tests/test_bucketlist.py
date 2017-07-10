import json
from flask_testing import TestCase
from app import create_app, db
from config import app_config


class TestBucketList(TestCase):
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

    # helper method fo registering a user
    def register_user(self):
        payload = {
            'username': 'Monica',
            'email': 'wahu@waru.com',
            'password': 'me'
        }
        self.client.post('api/v1/auth/register', data=json.dumps(payload), content_type='application/json')

    # helper method for login in a user
    def login_user(self):
        payload = {
            'username': 'Monica',
            'password': 'me'
        }
        r = self.client.post('api/v1/auth/login', data=json.dumps(payload), content_type='application/json')
        return json.loads(r.data.decode())['access_token']

    def test_bucketlist_creation(self):
        """Test API can create a bucketlist POST request"""
        self.register_user()
        access_token = self.login_user()
        body = {
            'name': 'Go to mombasa'
        }
        # create a bucketlist by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(body), content_type='application/json')
        self.assertEqual(r.status_code, 201)
        self.assertIn('Go to mombasa', json.loads(r.data.decode()).values())

    def test_get_all_bucketlists(self):
        """Test API can get a single bucketlist by using it's id."""
        # register a user in order to create a bucket list
        self.register_user()
        # get a token when a user log'sin
        access_token = self.login_user()
        body = {
            'name': 'Go to Mombasa'
        }
        # create a bucketlist by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(body), content_type='application/json')
        body = {
            'name': 'Paradise'
        }
        # create another bucketlist by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(body), content_type='application/json')

        item = {'name': 'Talk to Joho'}
        # create an item by making a POST request
        r = self.client.post(
            'api/va/bucketlists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(item), content_type='application/json')


        # get all bucketlists
        result = self.client.get(
            'api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token), content_type='application/json')

        self.assertEqual(result.status_code, 200)
        # check if the last bucketlist is the last bucketlist i posted
        self.assertIn('Paradise', json.loads(result.data.decode())['buckets'][-1].values())

    def test_get_bucketlist_by_id(self):
        """Test API can get a single bucketlist by using it's id."""
        self.register_user()
        access_token = self.login_user()
        body = {
            'name': 'Go to Mombasa'
        }
        # create a bucketlist by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(body), content_type='application/json')

        item = {'name': 'Talk to Joho'}
        # create an item by making a POST request
        self.client.post(
            'api/v1/bucketlists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(item), content_type='application/json')

        # get a bucket using id
        result = self.client.get(
            'api/v1/bucketlists/{}'.format(1),
            headers=dict(Authorization="Bearer " + access_token), content_type='application/json')
        # assert that the bucketlist is actually returned given its ID
        self.assertEqual(result.status_code, 200)
        self.assertIn('Go to Mombasa', json.loads(r.data.decode()).values())

    def test_get_bucketlist_by_id_that_does_not_exist(self):
        """Test API returns a 404 status code if there is no bucketlist with that id."""
        self.register_user()
        access_token = self.login_user()
        body = {
            'name': 'Go to Mombasa'
        }
        # create a bucketlist by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(body), content_type='application/json')

        # get a bucket using id
        result = self.client.get(
            'api/v1/bucketlists/{}'.format(45),
            headers=dict(Authorization="Bearer " + access_token), content_type='application/json')

        self.assertEqual(result.status_code, 404)


    def test_bucketlist_deletion(self):
        """Test API can delete an existing bucketlist. DELETE request."""
        self.register_user()
        access_token = self.login_user()
        body = {
            'name': 'Go to Mombasa'
        }
        # create a bucketlist by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(body), content_type='application/json')
        # delete the bucket using its ID
        r = self.client.delete(
            'api/v1/bucketlists/1',
            headers=dict(Authorization="Bearer " + access_token), content_type='application/json')
        self.assertEqual(r.status_code, 200)
        result = self.client.get(
            'api/v1/bucketlists/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)

    def test_bucketlist_can_be_edited(self):
        """Test API can edit an existing bucketlist. PUT request"""
        self.register_user()
        access_token = self.login_user()
        body = {
            'name': 'Go to Mombasa'
        }
        # create a bucketlist by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(body), content_type='application/json')
        # edit the post using PUT request
        result = self.client.put(
            'api/v1/bucketlists/1', data=json.dumps({'name': 'Go to Bujumbura'}),
            headers=dict(Authorization="Bearer " + access_token), content_type='application/json')
        # assert that the bucketlist is actually returned given its ID
        self.assertEqual(result.status_code, 200)
        self.assertIn('Go to Bujumbura', json.loads(result.data.decode()).values())

    def test_that_bucket_list_name_is_string(self):
        """Test API rejects the bucketlist name if its not a string"""
        self.register_user()
        access_token = self.login_user()
        body = {
            'name': {}
        }
        # create a bucketlist by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(body), content_type='application/json')
        self.assertEqual(r.status_code, 400)
        self.assertEqual("Name must be a string",json.loads(r.data.decode())['msg'])

    def test_post_with_a_bucketlist_name_that_already_exists(self):
        """Test API rejects bucketlist name if the user already have a bucketlist with the same name."""
        # register a user in order to create a bucket list
        self.register_user()
        # get a token when a user log'sin
        access_token = self.login_user()
        body = {
            'name': 'Go to Mombasa'
        }
        # create a bucketlist by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(body), content_type='application/json')
        body = {
            'name': 'Go to Mombasa'
        }
        # create another bucketlist by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(body), content_type='application/json')
        self.assertEqual('A bucket with that name already exists', json.loads(r.data.decode())['msg'])

    def test_can_create_item(self):
        # register a user in order to create a bucket list
        self.register_user()
        # get a token when a user log'sin
        access_token = self.login_user()
        body = {
            'name': 'Go to Mombasa'
        }
        # create a bucketlist by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(body), content_type='application/json')
        item = {
            'name': 'Swim at Diani'
        }
        # create an item by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(item), content_type='application/json')
        self.assertEqual(201, r.status_code)

    def test_can_get_all_items(self):
        # register a user in order to create a bucket list
        self.register_user()
        # get a token when a user log'sin
        access_token = self.login_user()
        body = {
            'name': 'Go to Mombasa'
        }
        # create a bucketlist by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(body), content_type='application/json')
        item = {
            'name': 'Swim at Diani'
        }
        # create an item by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(item), content_type='application/json')
        item2 = {'name':'Talk to Joho'}

        r = self.client.post(
            'api/v1/bucketlists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(item2), content_type='application/json')
        # get all items
        r = self.client.get(
            'api/v1/bucketlists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(item), content_type='application/json')

        self.assertIn('Talk to Joho', json.loads(r.data.decode())['items'][-1].values())

    def test_cant_create_two_same_items_in_bucketlist(self):
        # register a user in order to create a bucket list
        self.register_user()
        # get a token when a user log'sin
        access_token = self.login_user()
        body = {
            'name': 'Go to Mombasa'
        }
        # create a bucketlist by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(body), content_type='application/json')
        item = {
            'name': 'Swim at Diani'
        }
        # create an item by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(item), content_type='application/json')

        item = {
            'name': 'Swim at Diani'
        }
        # create an item by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(item), content_type='application/json')
        self.assertEqual(400, r.status_code)
        self.assertEqual('An Item with that name already exists', json.loads(r.data.decode())['msg'])

    def test_create_item_with_invalid_name(self):

        # register a user in order to create a bucket list
        self.register_user()
        # get a token when a user log'sin
        access_token = self.login_user()
        body = {
            'name': 'Go to Mombasa'
        }
        # create a bucketlist by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(body), content_type='application/json')
        item = {
            'name': {}
        }
        # create an item by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(item), content_type='application/json')

        self.assertEqual("Name must be a string", json.loads(r.data.decode())['msg'])

    def test_can_get_item(self):
        self.register_user()
        # get a token when a user log'sin
        access_token = self.login_user()
        body = {
            'name': 'Go to Mombasa'
        }
        # create a bucketlist by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(body), content_type='application/json')
        item = {
            'name': 'Talk to joho'
        }
        # create an item by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(item), content_type='application/json')
        self.assertEqual(r.status_code, 201)

        result = self.client.get(
            'api/v1/bucketlists/1/items/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Talk to joho', json.loads(result.data.decode()).values())

    def test_can_delete_item(self):
        self.register_user()
        # get a token when a user log'sin
        access_token = self.login_user()
        body = {
            'name': 'Go to Mombasa'
        }
        # create a bucketlist by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(body), content_type='application/json')
        item = {
            'name': 'Talk to joho'
        }
        # create an item by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(item), content_type='application/json')
        self.assertEqual(r.status_code, 201)

        r = self.client.delete(
            'api/v1/bucketlists/1/items/1',
            headers=dict(Authorization="Bearer " + access_token), content_type='application/json')

        result = self.client.get(
            'api/v1/bucketlists/1/items/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual('Item deleted successfully', json.loads(r.data.decode())['msg'])
        self.assertEqual(result.status_code, 404)



    def test_404(self):
        self.register_user()
        # get a token when a user log'sin
        access_token = self.login_user()
        r = self.client.get('api/v1/bucketlists/not/a/real/url',
            headers=dict(Authorization="Bearer " + access_token))

        self.assertEqual('Not found', json.loads(r.data.decode())['msg'])

    def test_wrong_bucket_id(self):
        self.register_user()
        # get a token when a user log'sin
        access_token = self.login_user()
        body = {
            'name': 'Go to Mombasa'
        }
        # create a bucketlist by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(body), content_type='application/json')
        item = {
            'name': 'Talk to joho'
        }
        # create an item by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(item), content_type='application/json')
        self.assertEqual(r.status_code, 201)

        r = self.client.get(
            'api/v1/bucketlists/2/items/1',
            headers=dict(Authorization="Bearer " + access_token), content_type='application/json')


        self.assertEqual('bucket not found', json.loads(r.data.decode())['msg'])

    def test_update_item(self):
        self.register_user()
        # get a token when a user log'sin
        access_token = self.login_user()
        body = {
            'name': 'Go to Mombasa'
        }
        # create a bucketlist by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(body), content_type='application/json')
        item = {
            'name': 'Talk to joho'
        }
        # create an item by making a POST request
        r = self.client.post(
            'api/v1/bucketlists/1/''items/',
            headers=dict(Authorization="Bearer " + access_token),
            data=json.dumps(item), content_type='application/json')
        self.assertEqual(r.status_code, 201)
        updete_item = {
            'name': 'Talk to Port',
            'done': 'True'
        }
        r = self.client.put(
            'api/v1/bucketlists/1/items/1',
            headers=dict(Authorization="Bearer " + access_token), data= json.dumps(updete_item), content_type='application/json')

        self.assertEqual('Item Updated successfully', json.loads(r.data.decode())['msg'])
