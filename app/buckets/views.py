import json
from flask import Blueprint, request, jsonify, abort
from app.models import User, Bucketlist, Item
from flask_jwt_extended import jwt_required,  get_jwt_identity
bucketlist = Blueprint("bucketlists", __name__, url_prefix='/')

@bucketlist.route('bucketlists/', methods=['POST', 'GET'])
@jwt_required
def bucketlists():

    user = User.query.filter_by(username=get_jwt_identity()).first()
    if request.method == 'POST':
        name = request.json.get('name', None)
        if not isinstance(name,str):
            return  jsonify({
                   "msg": "Name must be a string"
               }), 400 # bad request
        # check if the user has a bucketlist with the same name
        has_that_name = Bucketlist.query.filter_by(name=name).first()
        if has_that_name:

            return jsonify({
                "msg": "A bucket with that name already exists"
            }), 400  # bad request

        if name:
            bucketlist = Bucketlist(name=name, user_id=user.id)
            bucketlist.save()
            response = jsonify({
                'id': bucketlist.id,
                'name': bucketlist.name,
                'date_created': bucketlist.date_created,
                'date_modified': bucketlist.date_modified,
                'created_by': user.id
            })

            return response, 201

    else:
        # GET all the bucketlists created by this user

        bucketlists = Bucketlist.get_all_buckets_for_user(user.id)
        results = []

        for bucketlist in bucketlists:
            list_items =[]
            for item in bucketlist.items:
                item_to_dict  = {
                    'id': item.id,
                    'name': item.name,
                    'date_created': item.date_created,
                    'date_modified': item.date_modified,
                    'done': item.done,


                }
                list_items.append(item_to_dict)
            bucket = {
                'id': bucketlist.id,
                'name': bucketlist.name,
                'date_created': bucketlist.date_created,
                'date_modified': bucketlist.date_modified,
                'created_by': bucketlist.user,
                'items': list_items
            }
            results.append(bucket)

        return jsonify({'buckets':results}), 200

@bucketlist.route('bucketlists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required
def get_update_delete(id):
    bucketlist = Bucketlist.query.filter_by(id=id).first()
    if not bucketlist:
        # If there is no bucketlist
        # Raise an HTTPException with a 404 not found status code
        abort(404)

    if request.method == "DELETE":
        # delete the bucketlist using our delete method
        bucketlist.delete()
        return jsonify({
                   "msg": "bucketlist {} deleted".format(bucketlist.id)
               }), 200

    elif request.method == 'PUT':
        name = request.json.get('name', None)
        bucketlist.name = name
        bucketlist.update()

        response = {
            'id': bucketlist.id,
            'name': bucketlist.name,
            'date_created': bucketlist.date_created,
            'date_modified': bucketlist.date_modified,
            'created_by': bucketlist.user,
            'items': bucketlist.items
        }
        return jsonify(response), 200

    else:
        # Handle GET request, sending back the bucketlist to the user
        list_items = []
        for item in bucketlist.items:
            item_to_dict = {
                'id': item.id,
                'name': item.name,
                'date_created': item.date_created,
                'date_modified': item.date_modified,
                'done': item.done,

            }
            list_items.append(item_to_dict)
        response = {
            'id': bucketlist.id,
            'name': bucketlist.name,
            'date_created': bucketlist.date_created,
            'date_modified': bucketlist.date_modified,
            'created_by': bucketlist.user,
            'items': list_items
        }
        return jsonify(response), 200

@bucketlist.route('bucketlists/<int:id>/items/', methods=['GET', 'POST'])
@jwt_required
def bucketlist_items(id):
    bucketlist = Bucketlist.query.filter_by(id=id).first()
    if request.method == 'POST':
        name = request.json.get('name', None)
        if not isinstance(name, str):
            return jsonify({
                "msg": "Name must be a string"
            }), 400  # bad request
        # check if the user has a bucketlist with the same name
        has_that_name = Item.query.filter_by(name=name).first()
        if has_that_name:
            return jsonify({
                "msg": "An Item with that name already exists"
            }), 400  # bad request

        if name:
            item = Item(name=name, bucket_id=id)
            item.save()
            response = jsonify({
                'id': item.id,
                'name': item.name,
                'date_created': item.date_created,
                'date_modified': item.date_modified,
                'done': item.done
            })

            return response, 201

    else:

        items = Item.get_all_items(bucketlist_id=id)
        results = []

        for item in items:
            i = {
                'id': item.id,
                'name': item.name,
                'date_created': item.date_created,
                'date_modified': item.date_modified,
                'created_by': item.user,

            }
            results.append(i)

        return jsonify({'buckets': results}), 200

