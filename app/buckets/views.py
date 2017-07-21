from flask import Blueprint, request, jsonify, abort

from app.models import User, Bucketlist, Item
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import render_template

bucketlist = Blueprint("bucketlists", __name__, url_prefix='/api/v1/')


@bucketlist.route('bucketlists/', methods=['POST', 'GET'])
@jwt_required
def bucketlists():
    """Get all buckets and Create bucket"""
    user = User.query.filter_by(username=get_jwt_identity()).first()
    if request.method == 'POST':
        name = request.json.get('name', None)
        if not isinstance(name, str):
            return jsonify({
                "msg": "Name must be a string"
            }), 400  # bad request
        # check if the user has a bucketlist with the same name
        has_that_name = Bucketlist.query.filter_by(name=name, user=user.id).first()
        if has_that_name:
            return jsonify({
                "msg": "A bucket with that name already exists",

            }), 409  # conflict

        if name.strip():
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
            return jsonify({}), 400

    else:

        results = []
        limit = 20
        page = 1

        if request.args.get('limit') and request.args.get('limit').isdigit():
            limit = int(request.args.get('limit'))
            if limit < 1:
                limit = 20
            if limit > 100:
                limit = 100
        if request.args.get('page') and request.args.get('page').isdigit():
            page = int(request.args.get('page'))
            if page < 0:
                page = 1

        if request.args.get('q'):
            query = request.args.get('q')
            bucketlists = Bucketlist.query.filter_by(user=user.id).filter(
                Bucketlist.name.ilike("%" + query + "%")).paginate(page, limit, True)
        else:
            bucketlists = Bucketlist.query.filter_by(user=user.id).paginate(page, limit, True)

        for bucketlist in bucketlists.items:
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
            bucket = {
                'id': bucketlist.id,
                'name': bucketlist.name,
                'date_created': bucketlist.date_created,
                'date_modified': bucketlist.date_modified,
                'created_by': bucketlist.user,
                'items': list_items
            }
            results.append(bucket)

        return jsonify({'buckets': results}), 200


@bucketlist.route('bucketlists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required
def get_update_delete(id):
    """
    Get a bucket wiht id or delete the bucket or update the bucket
    :param id:
    :return:
    """

    user = User.query.filter_by(username=get_jwt_identity()).first()
    bucketlist = Bucketlist.query.filter_by(id=id, user=user.id).first()
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
        name = request.json.get('name')
        if name == bucketlist.name:
            return jsonify({
                'msg':"The Bucket cannot be updated with the same data"
            })
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
    """
    Get all items or Create an item
    :param id:
    :return:
    """

    user = User.query.filter_by(username=get_jwt_identity()).first()
    bucketlist = Bucketlist.query.filter_by(id=id, user=user.id).first()
    if not bucketlist:
        return jsonify({}), 400
    if request.method == 'POST':
        name = request.json.get('name')
        if name is None:
            return jsonify({
                "msg": "Provide key name"
            }), 400
        if not isinstance(name, str):
            return jsonify({
                "msg": "Name must be a string"
            }), 400  # bad request
        # check if the user has a bucketlist with the same name
        has_that_name = Item.query.filter_by(name=name).first()
        if has_that_name:
            return jsonify({
                "msg": "An Item with that name already exists"
            }), 409  # conflict

        if name.strip():
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
            return jsonify({
                "msg": "Provide key name"
            }), 400

    else:

        items = Item.get_all_items(bucketlist_id=id)
        results = []

        for item in items:
            i = { #
                'id': item.id,
                'name': item.name,
                'date_created': item.date_created,
                'date_modified': item.date_modified,
                'done': item.done,

            }
            results.append(i)

        return jsonify({'items': results}), 200


@bucketlist.route('bucketlists/<int:id>/items/<int:item_id>', methods=['GET', 'DELETE', 'PUT'])
@jwt_required
def get_delete_update_item(id, item_id):
    """
    Delete an item or update the item
    :param id:
    :param item_id:
    :return:
    """
    user = User.query.filter_by(username=get_jwt_identity()).first()
    bucketlist = Bucketlist.query.filter_by(id=id, user=user.id).first()

    if not bucketlist:
        return jsonify({'msg': 'bucket not found'}) ,404

    # get the item
    item = Item.query.filter_by(id=item_id, bucketlist=id).first()

    if not item:
        return jsonify({'msg': 'No item with that id'}), 404

    if request.method == 'DELETE':
        item.delete()
        return jsonify({
            "msg": "Item deleted successfully"
        }), 200

    if request.method == "PUT":
        name = request.json.get('name', None)
        done = request.json.get('done', None)
        if name == item.name:
            return jsonify({
                'msg':"The item cannot be updated with the same data"
            })
        if not (done and done.strip()) and not (name and name.strip()):
            return jsonify({'msg': 'Put something to update'}), 400
        if name and name.strip():
            item.name = name
        if done and done.strip():
            item.done = done

        item.update()
        return jsonify({'msg': 'Item Updated successfully'}), 201

    if request.method == "GET":
        response = jsonify({
            'id': item.id,
            'name': item.name,
            'date_created': item.date_created,
            'date_modified': item.date_modified,
            'done': item.done
        })

        return response, 201


@bucketlist.app_errorhandler(404)
def shika_izo_errors(e):
    return jsonify({"msg": "Not found"}), 404
