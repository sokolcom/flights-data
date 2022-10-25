from flask import Flask, request
from flask import make_response, jsonify, g

import flights_data
from .queries import *
# from .models import GrantedRole, Aircraft, Airport, Airline, Flight
from .balancer import YAML_AUTHORIZED_USERS, connect_db
from .caching import cache
from .errors import InvalidAPIUsage
from .loader import load_auth_users


app = Flask("flights-data")
# app.config.from_object(flights_data.config)


def db_connection(func):
    def wrapper():
        if not hasattr(g, 'db_link'):
            # if request.method == 'GET':
            #     g.db_link = connect_db(YAML_CONFIG_SLAVE, request.path)
            # else:
            #     g.db_link = connect_db(YAML_CONFIG_MASTER, request.path)
            g.db_link = connect_db(request.path)
            flights_data.models.db_proxy.initialize(g.db_link)
        return func()

    wrapper.__name__ = func.__name__
    return wrapper


def check_priveleges(func):
    def wrapper():
        response = None
        if request.method != 'GET':
            token = request.json["token"] if "token" in request.json else None
            if not token:
                response = make_response(jsonify({ "result": "401 - unauthorized", "ok": False }), 401)
            else:
                is_granted = token in load_auth_users(YAML_AUTHORIZED_USERS)["tokens"]
                # is_granted = (GrantedRole
                #     .select(GrantedRole.id)
                #     .where(GrantedRole.token == token)
                #     .exists()
                # )
                if not is_granted:
                    response = make_response(jsonify({ "result": "403 - forbidden", "ok": False }), 403)
                else:
                    response = func()
        else:
            response = func()

        return response

    wrapper.__name__ = func.__name__
    return wrapper


@app.teardown_appcontext
def disconnect_db(error):
    if hasattr(g, 'db_link'):
        g.db_link.close()


@app.route('/api/aircrafts', methods=['GET', 'POST', 'PUT', 'DELETE'])
@check_priveleges
@cache
@db_connection
def get_aircrafts():
    if request.method == 'GET':
        return get_aircrafts_query()
    else:
        return modify_aircrafts_query()


@app.route('/api/airports', methods=['GET', 'POST', 'PUT', 'DELETE'])
@check_priveleges
@cache
@db_connection
def get_airports():
    if request.method == 'GET':
        return get_airports_query()
    else:
        return modify_airports_query()


@app.route('/api/airlines', methods=['GET', 'POST', 'PUT', 'DELETE'])
@check_priveleges
@cache
@db_connection
def get_airlines():
    if request.method == 'GET':
        return get_airlines_query()
    else:
        return modify_airlines_query()


@app.route('/api/flights', methods=['GET', 'POST', 'PUT', 'DELETE'])
@check_priveleges
@cache
@db_connection
def get_flights():
    if request.method == 'GET':
        return get_flights_query()
    else:
        return modify_flights_query()


@app.route('/api/ac-operator', methods=['GET'])
@cache
@db_connection
def get_operator():
    return get_ac_operator_query()


@app.route('/api/avg-time', methods=['GET'])
@cache
@db_connection
def get_avg_time():
    return get_avgtime_query()


@app.errorhandler(404)
def page_not_found(error):
    return make_response(jsonify({ "result": "404 - not found", "ok": False }), 404)


@app.errorhandler(500)
def server_error():
    return jsonify({ "result": "500 - internal error", "ok": False })


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(e):
    return jsonify(e.to_dict())
