""" Here will be all the routes for the USER API """

# IMPORTS ==================================================
from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId
from bson.errors import InvalidId

from util.api_handler import APIHandler

from database.db import mongo


# SETTING ==================================================
# This is to have a "mapping" of these routes
# and make them reachable from other parts of the project
user_blueprint = Blueprint('user', __name__)  # '__name__' is 'routes.user' for this file


# ROUTES ===================================================
@user_blueprint.route('/user', methods=['POST'])
def create_user():
    """ Here I process the user data to then be stored"""

    user_data = request.json
    if not user_data:  # To validate the existence of actual data in the request
        return jsonify({'error': 'Missing data'}), 400

    # Now we will try to store tha new user in DB
    db_response = mongo.db.collection.insert_one(user_data)

    return jsonify({
        'result': 'success',
        'document_id': str(db_response.inserted_id)
    }), 201


# =============================================================
@user_blueprint.route('/user/<user_id>', methods=['GET'])
def get_user_info(user_id):
    """ Here I get the user info who lauch the request """

    try:
        # Convert the string user_id to an ObjectID
        object_id = ObjectId(user_id)
    except ImportError:
        return jsonify({'error': 'Invalid ID format'}), 400

    # Query the dabatase by _id
    document = mongo.db.collection.find_one({'_id': object_id})

    if document:
        # Convert the BSON document into a JSON object
        document['_id'] = str(document['_id'])  # Convert ObjectId to string for JSON serialization
        return jsonify(document), 200
    return jsonify({'error': 'User not found'}), 404


# =============================================================
@user_blueprint.route('/user/all/', methods=['GET'])
def get_all_users():
    """ Here I get the data for all users, for admin purposes """

    users = mongo.db.collection.find()
    users = [{**user, '_id': str(user['_id'])} for user in users]
    return jsonify({'users': users}), 200


# =============================================================
@user_blueprint.route('/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    """ Here update any data of the user """

    new_user_data = request.json  # Getting the data from the payload (request body)
    # If the request is empty {} here we handle the error
    if not new_user_data:
        return jsonify({'error': 'Data not provided'}), 400

    # Here we could check for the new_user_data content,
    # if it meets the expected requirements (fields and values)
    # TODO...

    # Attempt to convert user_id (string) into an ObjectId format
    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        return jsonify({'error': 'Invalid ID format'}), 400

    # Here we attempt to update the specified document with the specified new data
    db_response = mongo.db.collection.update_one({'_id': object_id}, {'$set': new_user_data})

    # 'matched_count' instead of 'modified_count' which remains in 0 if
    #  the new_user_data is exactly the same as the old one
    if db_response.matched_count:
        return jsonify({'result': 'Success updating user data'}), 200
    return jsonify({'error': 'User not found'}), 404


# =============================================================
@user_blueprint.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """ Here we delete any user specified in the request URL """

    # We need to convert the user_id into an ObjectID for Mongo treatments
    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        return jsonify({'error': 'Invalid ID format'}), 400

    # Here we try to delete the selected document
    db_response = mongo.db.collection.delete_one({'_id': object_id})

    if db_response.deleted_count:
        return jsonify({'result': 'Success at deleting the user'}), 200
    return jsonify({'error': 'User not found'}), 404


# =============================================================
@user_blueprint.route('/user/<user_id>/ghibli', methods=['GET'])
def ghibli_api_get_request(user_id):
    """
        Here each user can make a GET request through the Studio Ghibli API
        depending on their role as users of this current API
    """
    # Convert user_id from string to objectId for mongodb handling
    try:
        user_id = ObjectId(user_id)
    except ImportError as exc:
        print('Invalid User ID')
        raise ValueError from exc

    # Now we retrieve user role from db
    current_user = mongo.db.collection.find_one({'_id': user_id})
    current_user_role = current_user['role']

    # We handle the API requests here
    api_handler = APIHandler('https://ghibliapi.vercel.app')
    api_response = api_handler.get_data(current_user_role)

    # If there was an ERROR in the request
    if api_response['code'] != 200:
        return jsonify({
            'error': api_response['error']
        }), api_response['code']

    return jsonify({
        'status': 'success',
        'external_api_response': api_response
    })
