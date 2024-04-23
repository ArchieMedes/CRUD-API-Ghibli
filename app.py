"""
    Simple web app to try the Flask framwork
"""

# IMPORTS =====================================================
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.errors import InvalidId

app = Flask(__name__)

# MONGO DB CONFIGURATION
# 'mongo-db' is the service name in docker compose
app.config["MONGO_URI"] = "mongodb://mongo-db:27017/mydatabase"

mongo = PyMongo(app)

# ========= ROUTES ============================================
@app.route('/')
def health_check():
    """ Health check just that """
    return 'Service up and running!'


# =============================================================
@app.route('/user', methods=['POST'])
def create_user():
    """ Here I process the user data to then be stored"""

    user_data = request.json
    print("user_data:", user_data)
    if not user_data:  # to validate the existence of actual data in the request
        return jsonify({'error': 'Missing data'}), 400

    # now we will try to store tha new user in DB
    db_response = mongo.db.collection.insert_one(user_data)

    return jsonify({
        'result': 'success',
        'document_id': str(db_response.inserted_id)
    }), 201


# =============================================================
@app.route('/user/<user_id>', methods=['GET'])
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
@app.route('/user/all/', methods=['GET'])
def get_all_users():
    """ Here I get the data for all users, for admin purposes """

    users = mongo.db.collection.find()
    users = [{**user, '_id': str(user['_id'])} for user in users]
    return jsonify({'users': users}), 200


# =============================================================
@app.route('/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    """ Here update any data of the user """

    new_user_data = request.json  # getting the data from the payload (request body)
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

    # here we attempt to update the specified document with the specified new data
    db_response = mongo.db.collection.update_one({'_id': object_id}, {'$set': new_user_data})

    # 'matched_count' instead of 'modified_count' which remains in 0 if
    #  the new_user_data is exactly the same as the old one
    if db_response.matched_count:
        return jsonify({'result': 'Success updating user data'}), 200
    return jsonify({'error': 'User not found'}), 404


# =============================================================
@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """ Here we delete any user specified in the request URL """

    # we need to convert the user_id into an ObjectID for Mongo treatments
    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        return jsonify({'error': 'Invalid ID format'}), 400

    # Here we try to delete the selected document
    db_response = mongo.db.collection.delete_one({'_id': object_id})

    if db_response.deleted_count:
        return jsonify({'result': 'Success at deleting the user'}), 200
    return jsonify({'error': 'User not found'}), 404
