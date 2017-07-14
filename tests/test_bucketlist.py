import json
from flask_testing import TestCase
from app import create_app, db
from config import app_config
from flask import url_for


class TestBucketList(TestCase):
    def create_app(self):
        app = self.app = create_app(app_config['testing'])
        return app

    # helper method fo registering a user
    def register_user(self):
        payload = {
            'username': 'Monica',
            'email': 'wahu@waru.com',
            'password': 'm24523452345e'
        }
        self.client.post(url_for('auth.register'), data=json.dumps(payload), content_type='application/json')

    # helper method for login in a user
    def login_user(self):
        payload = {
            'username': 'Monica',
            'password': 'm24523452345e'
        }

        re = self.client.post(url_for('auth.login'), data=json.dumps(payload), content_type='application/json')
        return json.loads(re.data.decode())['access_token']

    def setUp(self):
        # create a client for making posts
        self.client = self.create_app().test_client()

        # This will create the database file using SQLAlchemy
        db.create_all()

        self.register_user()

        self.access_token = self.login_user()

        self.id = '1'

        self.body = {
            'name': 'Go to mombasa'
        }
        self.item = {
            'name': 'Swim at Diani'
        }

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_invalid_token(self):
        self.access_token += 'Bad Token'
        r = self.client.post(
            url_for('bucketlists.bucketlists'),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.body), content_type='application/json')

        self.assertIn('Bad Authorization header', json.loads(r.data.decode())['msg'])


    def test_bucketlist_creation(self):
        """Test API can create a bucketlist POST request"""
        # create a bucketlist by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlists'),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.body), content_type='application/json')
        self.assertEqual(r.status_code, 201)
        self.assertIn('Go to mombasa', json.loads(r.data.decode()).values())

    def test_get_all_bucketlists(self):
        """Test API can get a single bucketlist by using it's id."""
        # create a bucketlist by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlists'),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.body), content_type='application/json')

        # get all bucketlists
        result = self.client.get(
            url_for('bucketlists.bucketlists'),
            headers=dict(Authorization="Bearer " + self.access_token), content_type='application/json')

        self.assertEqual(result.status_code, 200)
        self.assertIn('Go to mombasa', json.loads(result.data.decode())['buckets'][0].values())

    def test_get_bucketlist_by_id(self):
        """Test API can get a single bucketlist by using it's id."""

        # create a bucketlist by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlists'),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.body), content_type='application/json')

        # get a bucket using id
        result = self.client.get(
            url_for('bucketlists.get_update_delete', id=self.id),
            headers=dict(Authorization="Bearer " + self.access_token), content_type='application/json')
        # assert that the bucketlist is actually returned given its ID
        self.assertEqual(result.status_code, 200)
        self.assertIn('Go to mombasa', json.loads(result.data.decode()).values())

    def test_get_bucketlist_by_id_that_does_not_exist(self):
        """Test API returns a 404 status code if there is no bucketlist with that id."""

        # get a bucket using id
        result = self.client.get(
            url_for('bucketlists.get_update_delete', id=self.id) ,
            headers=dict(Authorization="Bearer " + self.access_token), content_type='application/json')

        self.assertEqual(result.status_code, 404)
        self.assertEqual('Not found', json.loads(result.data.decode())['msg'])


    def test_bucketlist_deletion(self):
        """Test API can delete an existing bucketlist. DELETE request."""

        # create a bucketlist by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlists'),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.body), content_type='application/json')
        # delete the bucket using its ID

        r = self.client.delete(
            url_for('bucketlists.get_update_delete', id=self.id) ,
            headers=dict(Authorization="Bearer " + self.access_token), content_type='application/json')

        self.assertEqual(r.status_code, 200)
        self.assertEqual('bucketlist 1 deleted', json.loads(r.data.decode())['msg'])

        result = self.client.get(
            url_for('bucketlists.get_update_delete', id=self.id),
            headers=dict(Authorization="Bearer " + self.access_token))
        self.assertEqual(result.status_code, 404)
        self.assertEqual('Not found', json.loads(result.data.decode())['msg'])

    def test_bucketlist_can_be_edited(self):
        """Test API can edit an existing bucketlist. PUT request"""

        # create a bucketlist by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlists'),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.body), content_type='application/json')
        # edit the post using PUT request
        result = self.client.put(
            url_for('bucketlists.get_update_delete', id=self.id), data=json.dumps({'name': 'Go to Bujumbura'}),
            headers=dict(Authorization="Bearer " + self.access_token), content_type='application/json')
        # assert that the bucketlist is actually returned given its ID
        self.assertEqual(result.status_code, 200)
        self.assertIn('Go to Bujumbura', json.loads(result.data.decode()).values())

    def test_that_bucket_list_name_is_string(self):
        """Test API rejects the bucketlist name if its not a string"""
        self.body['name'] = 90
        # create a bucketlist by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlists'),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.body), content_type='application/json')
        self.assertEqual(r.status_code, 400)
        self.assertEqual("Name must be a string", json.loads(r.data.decode())['msg'])

    def test_post_with_a_bucketlist_name_that_already_exists(self):
        """Test API rejects bucketlist name if the user already have a bucketlist with the same name."""
        # register a user in order to create a bucket list

        # create a bucketlist by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlists'),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.body), content_type='application/json')

        # create another bucketlist by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlists'),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.body), content_type='application/json')

        self.assertEqual(r.status_code, 409)
        self.assertEqual('A bucket with that name already exists', json.loads(r.data.decode())['msg'])

    def test_can_create_item(self):
        # register a user in order to create a bucket list

        # create a bucketlist by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlists'),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.body), content_type='application/json')

        # create an item by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlist_items',id=self.id),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.item), content_type='application/json')

        self.assertEqual(201, r.status_code)

    def test_can_get_all_items(self):
        # create a bucketlist by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlists'),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.body), content_type='application/json')

        # create an item by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlist_items',id=self.id),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.item), content_type='application/json')

        # get all items
        r = self.client.get(
            url_for('bucketlists.bucketlist_items',id=self.id),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.item), content_type='application/json')

        self.assertEqual(200, r.status_code)
        self.assertIn('Swim at Diani', json.loads(r.data.decode())['items'][-1].values())

    def test_cant_create_two_same_items_in_bucketlist(self):

        # create a bucketlist by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlists'),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.body), content_type='application/json')

        # create an item by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlist_items',id=self.id),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.item), content_type='application/json')

        # Try to create the same item by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlist_items',id=self.id),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.item), content_type='application/json')

        self.assertEqual(400, r.status_code)
        self.assertEqual('An Item with that name already exists', json.loads(r.data.decode())['msg'])

    def test_create_item_with_invalid_name(self):
        # create a bucketlist by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlists'),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.body), content_type='application/json')

        self.item['name'] = {}
        # create an item by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlist_items',id=self.id),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.item), content_type='application/json')
        self.assertEqual(400, r.status_code)
        self.assertEqual("Name must be a string", json.loads(r.data.decode())['msg'])

    def test_can_get_item(self):
        # create a bucketlist by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlists'),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.body), content_type='application/json')

        # create an item by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlist_items',id=self.id),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.item), content_type='application/json')

        result = self.client.get(
            url_for('bucketlists.get_delete_update_item',id=self.id, item_id=self.id),
            headers=dict(Authorization="Bearer " + self.access_token))
        self.assertEqual(r.status_code, 201)
        self.assertIn('Swim at Diani', json.loads(result.data.decode()).values())

    def test_can_delete_item(self):
        # create a bucketlist by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlists'),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.body), content_type='application/json')

        # create an item by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlist_items',id=self.id),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.item), content_type='application/json')

        r = self.client.delete(
            url_for('bucketlists.get_delete_update_item',id=self.id, item_id=self.id),
            headers=dict(Authorization="Bearer " + self.access_token), content_type='application/json')

        result = self.client.get(
            url_for('bucketlists.get_delete_update_item',id=self.id, item_id=self.id),
            headers=dict(Authorization="Bearer " + self.access_token))
        self.assertEqual('Item deleted successfully', json.loads(r.data.decode())['msg'])
        self.assertEqual(result.status_code, 404)

    def test_404_error_returns_json(self):
        r = self.client.get('api/v1/bucketlists/not/a/real/url',
                            headers=dict(Authorization="Bearer " + self.access_token))

        self.assertEqual('Not found', json.loads(r.data.decode())['msg'])
        self.assertEqual(r.status_code, 404)

    def test_wrong_bucket_id(self):
        # create a bucketlist by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlists'),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.body), content_type='application/json')

        # create an item by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlist_items', id=self.id),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.item), content_type='application/json')

        self.assertEqual(r.status_code, 201)

        r = self.client.get(
            url_for('bucketlists.get_delete_update_item',id=self.id , item_id=self.id),
            headers=dict(Authorization="Bearer " + self.access_token), content_type='application/json')
        self.assertEqual(r.status_code, 404)
        self.assertEqual('bucket not found', json.loads(r.data.decode())['msg'])

    def test_update_item(self):
        # create a bucketlist by making a POST request
        r = self.client.post(
            url_for('bucketlists.bucketlists'),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.body), content_type='application/json')

        # create an item by making a POST request
        r = self.client.post(
             url_for('bucketlists.bucketlist_items',id=self.id),
            headers=dict(Authorization="Bearer " + self.access_token),
            data=json.dumps(self.item), content_type='application/json')
        self.assertEqual(r.status_code, 201)

        # Change the name of the item
        self.item['name'] = 'Talk to Port'

        r = self.client.put(
            url_for('bucketlists.get_delete_update_item',id=self.id, item_id=self.id),
            headers=dict(Authorization="Bearer " + self.access_token), data=json.dumps(self.item),
            content_type='application/json')

        self.assertEqual('Item Updated successfully', json.loads(r.data.decode())['msg'])
        self.assertEqual(r.status_code, 201)
