import datetime as dt

from flask import Blueprint
from flask_api import status
from flask import request, jsonify
from functools import wraps

from config import Parser
from database.mongo_helper import MongoHelper
from database.classes import Item, Event, Sensor, User, Token, Map, USER_ACCESS_MASTER, USER_ACCESS_DEFAULT, \
    USER_ACCESS_LIMITED
from google_utils import get_google_user_data

mongo_helper = MongoHelper.init_from_config(Parser())

bp = Blueprint(__name__, 'api_v1')


def secure_token(restrict_access=USER_ACCESS_LIMITED):
    # por padrao, qualquer nivel de acesso tem permissão na rota
    # 401 - fora da lista
    # 403 - sem acesso (permissao)
    # 498 - token expirado
    def decorator(f):
        @wraps(f)
        def check_authorization(*args, **kwargs):
            if not request.headers.get("Authorization"):
                return jsonify({"Error": "No authorization token supplied"}), status.HTTP_401_UNAUTHORIZED

            if "bearer" in request.headers.get("Authorization"):
                try:
                    token = Token(mongo_helper, _id=request.headers.get("Authorization")[7:])
                    token.update_token()

                    if token['access_level'] <= restrict_access:
                        return f(*args, **kwargs)
                    else:
                        return jsonify(
                            {"Error": "User does not have access to this resource"}), status.HTTP_403_FORBIDDEN

                except ValueError:
                    return jsonify({"Error": "Token expired", "Reason": str(e), "Authorization": request.headers.get("Authorization")}), 498
            else:
                return jsonify({"Error": "Token in the wrong format supplied"}), status.HTTP_401_UNAUTHORIZED

        return check_authorization

    return decorator

ALERT_UNREAD = 1
ALERT_READ = 2
@bp.route('/event', methods=('POST',))
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

        alert = None
        if item.get("location_blacklist"):
            loc_blacklist = item["location_blacklist"]
            if isinstance(loc_blacklist, list):
                if sensor_id in loc_blacklist:
                    alert = ALERT_UNREAD
            else:
                if sensor_id == loc_blacklist:
                    alert = ALERT_UNREAD

        if item.get("location_whitelist"):
            loc_whitelist = item["location_whitelist"]
            if isinstance(loc_whitelist, list):
                if sensor_id not in loc_whitelist:
                    alert = ALERT_UNREAD
            else:
                if sensor_id != loc_whitelist:
                    alert = ALERT_UNREAD

        r = mongo_helper.add_event(sensor_id, tag_id, item["item_id"], event_timestamp, event_details, alert)
        return jsonify({"Event added successfully": str(r.inserted_id)}), status.HTTP_200_OK


@bp.route('/event', methods=('GET',))
@secure_token()
def read_event():
    if request.method == "GET":
        sensor_id = request.args.get('sensor_id')
        item_id = request.args.get('item_id')
        start_timestamp_range = request.args.get('start_timestamp_range')
        end_timestamp_range = request.args.get('end_timestamp_range')
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))

        events = Event(mongo_helper).filter_events(sensor_id, item_id, start_timestamp_range, end_timestamp_range, limit, skip)
        return jsonify([dict(x) for x in events]), status.HTTP_200_OK


@bp.route('/event_count', methods=('GET',))
@secure_token()
def get_event_count():
    return jsonify({"event_count": Event(mongo_helper).count()}), status.HTTP_200_OK


@bp.route('/sensor', methods=('POST',))
@secure_token(USER_ACCESS_DEFAULT)
def create_sensor():
    if request.method == 'POST':
        try:
            sensor = Sensor(mongo_helper).create_from_request(request)
            return jsonify({"Message": "Inserted Successfully!", "sensor": dict(sensor)}), status.HTTP_200_OK
        except Exception as e:
            return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST


@bp.route('/sensor', methods=('GET',))
@secure_token()
def read_sensor():
    if request.method == 'GET':
        return jsonify(Sensor(mongo_helper).get_all()), status.HTTP_200_OK


@bp.route('/sensor/<sensor_id>', methods=('GET',))
@secure_token()
def find_sensor(sensor_id):
    if request.method == 'GET':
        try:
            sensor = Sensor(mongo_helper, sensor_id)
            return jsonify(dict(sensor)), status.HTTP_200_OK
        except Exception as e:
            return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST


@bp.route('/sensor/<sensor_id>', methods=('PUT', 'DELETE'))
@secure_token(restrict_access=USER_ACCESS_DEFAULT)
def update_sensor(sensor_id):
    if request.method == 'PUT':
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


@bp.route('/item', methods=('POST',))
@secure_token(restrict_access=USER_ACCESS_DEFAULT)
def create_item():
    try:
        item = Item(mongo_helper).create_from_request(request)
        return jsonify({"Message": "Inserted Successfully!", "item": dict(item)}), status.HTTP_200_OK
    except Exception as e:
        return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST


@bp.route('/item/<item_id>', methods=('GET',))
@secure_token()
def find_item(item_id):
    if request.method == 'GET':
        try:
            item = Item(mongo_helper, item_id)
            return jsonify(dict(item)), status.HTTP_200_OK
        except Exception as e:
            return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST


@bp.route('/item/<item_id>', methods=('PUT', 'DELETE'))
@secure_token(restrict_access=USER_ACCESS_DEFAULT)
def update_item(item_id):
    if request.method == 'PUT':
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
@secure_token()
def search_item():
    query = request.json.get('query')
    history_limit = request.json.get('history_limit', 10)
    history_skip = request.json.get('history_skip', 0)
    result_set = Item(mongo_helper).search(query)
    # joining events
    for item in result_set:
        item["last_activity"] = Event(mongo_helper).filter_events(item_id=item["item_id"], limit=history_limit, skip=history_skip) or None
    return jsonify(result_set), status.HTTP_200_OK


@bp.route('/search/sensor', methods=('POST',))
@secure_token()
def search_sensor():
    query = request.json.get('query')
    history_limit = request.json.get('history_limit', 10)
    history_skip = request.json.get('history_skip', 0)
    result_set = Sensor(mongo_helper).search(query)
    # joining events
    for sensor in result_set:
        sensor["last_activity"] = Event(mongo_helper).filter_events(sensor_id=sensor["sensor_id"], limit=history_limit, skip=history_skip) or None
    return jsonify(result_set), status.HTTP_200_OK


@bp.route('/search/event', methods=('POST',))
@secure_token()
def search_event():
    start_timestamp_range = request.json.get('start_timestamp_range')
    end_timestamp_range = request.json.get('end_timestamp_range')
    limit = int(request.json.get('limit', 0))
    skip = int(request.json.get('skip', 0))

    alert_only = request.json.get('alert_only')

    sensor_queries = request.json.get('sensor_query')
    result_sensors = None
    if sensor_queries:
        result_sensors = Sensor(mongo_helper).search(sensor_queries, return_objects=True)

    item_queries = request.json.get('item_query')
    result_items = None
    if item_queries:
        result_items = Item(mongo_helper).search(item_queries, return_objects=True)

    events = Event(mongo_helper).filter_events(
        ([x["sensor_id"] for x in result_sensors] if result_sensors is not None else result_sensors),
        ([x["item_id"] for x in result_items] if result_items is not None else result_items),
        start_timestamp_range, end_timestamp_range, limit, skip, alert_only)


    results = []
    for event in events:
        e = dict(event)
        e["sensor"] = dict(Sensor(mongo_helper, e["sensor_id"]))
        e["item"] = dict(Item(mongo_helper, e["item_id"]))
        results.append(e)

    return jsonify(results), status.HTTP_200_OK


@bp.route('/user', methods=('POST', 'GET'))
@secure_token(restrict_access=USER_ACCESS_MASTER)
def create_user():
    if request.method == 'GET':
        return jsonify(User(mongo_helper).get_all()), status.HTTP_200_OK
    elif request.method == 'POST':
        try:
            item = User(mongo_helper).create_from_request(request)
            return jsonify({"Message": "Inserted Successfully!", "item": dict(item)}), status.HTTP_200_OK
        except Exception as e:
            return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST


@bp.route('/user/<email>', methods=('DELETE', 'GET', 'PUT'))
@secure_token(restrict_access=USER_ACCESS_MASTER)
def manage_user(email):
    if request.method == 'GET':
        try:
            user = User(mongo_helper, email)
            return jsonify(dict(user)), status.HTTP_200_OK
        except Exception as e:
            return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST
    elif request.method == 'PUT':
        try:
            user = User(mongo_helper, email)
            user.update_from_request(request)
            return jsonify(dict(user)), status.HTTP_200_OK
        except Exception as e:
            return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST
    elif request.method == 'DELETE':
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

    # Check if e-mail supplied matches google token supplied
    g_user_data = get_google_user_data(access_token)
    if g_user_data["email"].lower() != email.lower():
        return jsonify({
            "success": False
        }), status.HTTP_401_UNAUTHORIZED

    if User(mongo_helper).count() == 0:  # There is no user registered. Register this user as admin so he can enable others in
        User(mongo_helper).create_from_raw_data({
            "email": email,
            "access": USER_ACCESS_MASTER
        })
    try:
        user = User(mongo_helper, email)
        user_data = dict(user)
        user_data["id_token"] = id_token
        user_data["access_token"] = access_token
        user_data["google_data"] = g_user_data
        access_token = Token(mongo_helper).create_token_from_user_data(user_data)

        return jsonify({
           "success": True,
           "access_token": access_token
        }), status.HTTP_200_OK
    except ValueError:  # User not in database
        return jsonify({
            "success": False
        }), status.HTTP_401_UNAUTHORIZED


@bp.route('/map', methods=('POST',))
#@secure_token(restrict_access=USER_ACCESS_MASTER)
def create_map():
    try:
        item = Map(mongo_helper).create_from_request(request)
        return jsonify({"Message": "Inserted Successfully!", "item": dict(item)}), status.HTTP_200_OK
    except Exception as e:
        return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST


@bp.route('/map/<name>', methods=('DELETE', 'GET', 'PUT'))
#@secure_token(restrict_access=USER_ACCESS_MASTER)
def manage_map(name):
    if request.method == 'GET':
        try:
            user = Map(mongo_helper, name)
            return jsonify(dict(user)), status.HTTP_200_OK
        except Exception as e:
            return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST
    elif request.method == 'PUT':
        try:
            map_item = Map(mongo_helper, name)
            map_item.update_from_request(request)
            return jsonify(dict(map_item)), status.HTTP_200_OK
        except Exception as e:
            return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST
    elif request.method == 'DELETE':
        try:
            map_item = Map(mongo_helper, name)
            map_item.delete()
            return jsonify({'Message': "Map removed successfully"}), status.HTTP_200_OK
        except Exception as e:
            return jsonify({'Message': str(e)}), status.HTTP_400_BAD_REQUEST
