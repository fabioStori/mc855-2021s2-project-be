import datetime as dt
import json

from flask import Blueprint
from flask_api import status
from flask import request, jsonify
from functools import wraps

from config import Parser
from database.mongo_helper import MongoHelper
from database.classes import Item, Event, Sensor, User

mongo_helper = MongoHelper.init_from_config(Parser())

bp = Blueprint(__name__, 'api_v1')


def secure_token(f):
    @wraps(f)
    def check_authorization(*args, **kwargs):
        if not request.headers.get("Authorization"):
            return jsonify({"Error": "No authorization token supplied"}), status.HTTP_401_UNAUTHORIZED

        if "bearer" in request.headers.get("Authorization"):
            # TODO validate the token in the bearer field
            return f(*args, **kwargs)
        else:
            return jsonify({"Error": "Token in the wrong format supplied"}), status.HTTP_401_UNAUTHORIZED

    return check_authorization


@bp.route('/event', methods=('POST', 'GET'))
@secure_token
def register_event():
    if request.method == "POST":
        sensor_id = request.json.get('sensor_id')
        tag_id = request.json.get('tag_id')
        event_timestamp = request.json.get('event_timestamp')
        event_details = request.json.get('event_details')

        if not sensor_id or not tag_id or not event_timestamp:
            return jsonify({"error": "missing fields for registration"}), status.HTTP_400_BAD_REQUEST

        sensor = mongo_helper.get_sensor(sensor_id)
        if not sensor:
            return jsonify({"error": "sensor not registered"}), status.HTTP_400_BAD_REQUEST

        item = mongo_helper.get_item_by_tag(tag_id)
        if not item:
            return jsonify({"error": "no item registered for this tag"}), status.HTTP_400_BAD_REQUEST

        r = mongo_helper.add_event(sensor_id, tag_id, item["item_id"], event_timestamp, event_details)
        return jsonify({"Event added successfully": str(r.inserted_id)}), status.HTTP_200_OK

    elif request.method == "GET":
        sensor_id = request.json.get('sensor_id')
        item_id = request.json.get('item_id')
        start_timestamp_range = request.json.get('start_timestamp_range')
        end_timestamp_range = request.json.get('end_timestamp_range')

        events = Event(mongo_helper).filter(sensor_id, item_id, start_timestamp_range, end_timestamp_range)
        return jsonify([dict(x) for x in events]), status.HTTP_200_OK


@bp.route('/event_count', methods=('GET',))
@secure_token
def get_event_count():
    return jsonify({"event_count": Event(mongo_helper).count()}), status.HTTP_200_OK


@bp.route('/sensor', methods=('POST', 'GET'))
@secure_token
def create_sensor():
    if request.method == 'POST':
        try:
            sensor = Sensor(mongo_helper).create_from_request(request)
            return jsonify({"Message": "Inserted Successfully!", "sensor": dict(sensor)}), status.HTTP_200_OK
        except Exception as e:
            return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST
    elif request.method == 'GET':
        return jsonify(Sensor(mongo_helper).get_all()), status.HTTP_200_OK


@bp.route('/sensor/<sensor_id>', methods=('GET', 'PUT', 'DELETE'))
@secure_token
def find_sensor(sensor_id):
    if request.method == 'GET':
        try:
            sensor = Sensor(mongo_helper, sensor_id)
            return jsonify(dict(sensor)), status.HTTP_200_OK
        except Exception as e:
            return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST
    elif request.method == 'PUT':
        try:
            sensor = Sensor(mongo_helper, sensor_id)
            sensor.update_from_request(request)
            return jsonify(dict(sensor)), status.HTTP_200_OK
        except Exception as e:
            return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST
    elif request.method == 'DELETE':
        try:
            sensor = Sensor(mongo_helper, sensor_id)
            sensor.delete()
            return jsonify({'Message': "Sensor removed successfully"}), status.HTTP_200_OK
        except Exception as e:
            return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST


@bp.route('/item', methods=('POST', ))
@secure_token
def create_item():
    try:
        item = Item(mongo_helper).create_from_request(request)
        return jsonify({"Message": "Inserted Successfully!", "item": dict(item)}), status.HTTP_200_OK
    except Exception as e:
        return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST


@bp.route('/item/<item_id>', methods=('GET', 'PUT', 'DELETE'))
@secure_token
def find_item(item_id):
    if request.method == 'GET':
        try:
            item = Item(mongo_helper, item_id)
            return jsonify(dict(item)), status.HTTP_200_OK
        except Exception as e:
            return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST
    elif request.method == 'PUT':
        try:
            item = Item(mongo_helper, item_id)
            item.update_from_request(request)
            return jsonify(dict(item)), status.HTTP_200_OK
        except Exception as e:
            return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST
    elif request.method == 'DELETE':
        try:
            item = Item(mongo_helper, item_id)
            item.delete()
            return jsonify({'Message': "Item removed successfully"}), status.HTTP_200_OK
        except Exception as e:
            return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST


@bp.route('/search/item', methods=('POST',))
@secure_token
def search_item():
    query = request.json.get('query')
    return jsonify(Item(mongo_helper).search(query)), status.HTTP_200_OK


@bp.route('/search/sensor', methods=('POST',))
@secure_token
def search_sensor():
    query = request.json.get('query')
    return jsonify(Sensor(mongo_helper).search(query)), status.HTTP_200_OK


@bp.route('/user', methods=('POST',))
def create_user():
    try:
        # a ideia eh tirar essa verificacao daqui e colocar dentro do classes se der
        if request.json.get('access') not in ['limited', 'default', 'master']:
            return jsonify({'Message': 'Invalid access type'}), status.HTTP_400_BAD_REQUEST
        request.json['creation_date'] = dt.datetime.now()
        item = User(mongo_helper).create_from_request(request)
        return jsonify({"Message": "Inserted Successfully!", "item": dict(item)}), status.HTTP_200_OK
    except Exception as e:
        return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST


@bp.route('/user/<email>', methods=('DELETE', 'GET'))
def manage_user(email):
    if request.method == 'DELETE':
        try:
            user = User(mongo_helper, email)
            user.delete()
            return jsonify({'Message': "User removed successfully"}), status.HTTP_200_OK
        except Exception as e:
            return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST

@bp.route('/login', methods=('POST',))
def login():
    id_token = request.json.get('id_token')
    access_token = request.json.get('access_token')
    email = request.json.get('email')
    allowed_users = [
        'f196631@dac.unicamp.br',
        'f171036@dac.unicamp.br',
        'g172111@dac.unicamp.br',
        'a193325@dac.unicamp.br',
        'jufborin@unicamp.br',
        'soraia@ic.unicamp.br',
    ]

    if email in allowed_users:
        return jsonify({
            "success": True,
            "access_token": "ABCD1234"
        }), status.HTTP_200_OK
    else:
        return jsonify({
            "success": False
        }), status.HTTP_401_UNAUTHORIZED

