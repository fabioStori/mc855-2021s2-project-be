import json
import uuid
import base64
from flask import Blueprint
from flask_api import status
from flask import request, jsonify
from functools import wraps

from config import Parser
from database.mongo_helper import MongoHelper

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

    return check_authorization


@bp.route('/event', methods=('POST',))
@secure_token
def register_event():
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


@bp.route('/event_count', methods=('GET',))
def get_event_count():
    return jsonify({"event_count": mongo_helper.get_event_count()}), status.HTTP_200_OK


@bp.route('/sensor', methods=('POST',))
def create_sensor():
    try:
        data = {
            'sensor_name': request.json.get('name'),
            'patrimony_number': request.json.get('number'),
            'description': request.json.get('description'),
            'sensor_id': request.json.get('id'),
            'type': request.json.get('type')
        }
        mongo_helper.add_sensor(data)
        return jsonify({"Message": "Inserted!"}), status.HTTP_200_OK
    except ValueError:
        return jsonify({'Message': ValueError}), status.HTTP_400_BAD_REQUEST

@bp.route('/sensor/<sensor_id>', methods=('GET',))
def find_sensor(sensor_id):
    try:
        response = mongo_helper.get_sensor(sensor_id)
        del response['_id']
        return jsonify(response), status.HTTP_200_OK
    except ValueError:
        return jsonify({'Message': ValueError}), status.HTTP_400_BAD_REQUEST


@bp.route('/item', methods=('POST',))
def create_item():
    try:
        data = {
            'item_name': request.json.get('name'),
            'patrimony_number': request.json.get('number'),
            'safehouse': request.json.get('safehouse'),
            'item_id': request.json.get('item_id'),
            'type': request.json.get('type')
        }
        response = mongo_helper.add_item(data)
        return jsonify({"Message": response}), status.HTTP_200_OK
    except ValueError:
        return jsonify({'Message': ValueError}), status.HTTP_400_BAD_REQUEST

@bp.route('/item/<item_id>', methods=('GET',))
def find_item(item_id):
    try:
        response = mongo_helper.get_item(item_id)
        print(response)
        del response['_id']
        return jsonify(response), status.HTTP_200_OK
    except ValueError:
        return jsonify({'Message': ValueError}), status.HTTP_400_BAD_REQUEST