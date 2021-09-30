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
    event_details = request.json.get('event_details')

    if not sensor_id or not tag_id:
        return jsonify({"error": "missing fields for registration"}), status.HTTP_400_BAD_REQUEST

    return jsonify({"event_data": event_details}), status.HTTP_200_OK


@bp.route('/event_count', methods=('GET',))
def get_event_count():
    return jsonify({"event_count": mongo_helper.get_event_count()}), status.HTTP_200_OK
