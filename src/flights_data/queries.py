import datetime as dt
from flask import Flask, request
from flask import make_response, jsonify, g
import peewee as orm

from .models import Aircraft, Airport, Airline, Flight
from .errors import InvalidAPIUsage


__all__ = [
    "get_aircrafts_query", "modify_aircrafts_query",
    "get_airports_query", "modify_airports_query",
    "get_airlines_query", "modify_airlines_query",
    "get_flights_query", "modify_flights_query",
    "get_ac_operator_query",
    "get_avgtime_query"
]

DEFAULT_BULKSIZE = 10

AC_REQUIRED_FIELDS = { "tail_no", "mfr", "model", "photo" }
AL_REQUIRED_FIELDS = { "airline_id", "fullname", "addr", "phone_no" }
AP_REQUIRED_FIELDS = { "iata", "fullname", "city", "state", "country", "lat", "lng" }
FL_REQUIRED_FIELDS = {
    "flight_date", "day_of_week", "tail_no", "airline_id", "flight_id", 
    "origin", "dest", "dist", "delayed", "diverted", "cancelled"
}

AC_ALL_FIELDS = { "tail_no", "mfr", "model", "bday", "photo" }
AL_ALL_FIELDS = { "airline_id", "fullname", "addr", "phone_no" }
AP_ALL_FIELDS = { "iata", "fullname", "city", "state", "country", "lat", "lng" }
FL_ALL_FIELDS = {
    "id", "flight_date", "day_of_week", "tail_no", "airline_id", "flight_id", "origin", 
    "dest", "dist", "delayed", "diverted", "cancelled", "scheduled_time", "real_time"
}

fields_mapping = {
    Aircraft: { "all": AC_ALL_FIELDS, "req": AC_REQUIRED_FIELDS, "pk": "tail_no" },
    Airport: { "all": AP_ALL_FIELDS, "req": AP_REQUIRED_FIELDS, "pk": "iata" }, 
    Airline: { "all": AL_ALL_FIELDS, "req": AL_REQUIRED_FIELDS, "pk": "airline_id" },
    Flight: { "all": FL_ALL_FIELDS, "req": FL_REQUIRED_FIELDS, "pk": "id" },
}


def _get_fields(all_fields):
    content = request.json
    content.pop("token")
    if not all_fields.issuperset(set(content.keys())):
        raise InvalidAPIUsage("wrong keys", status_code=404)
    
    return content


def _post_query(model):
    fields = _get_fields(fields_mapping[model]["all"])
    if fields_mapping[model]["req"] != set(fields.keys()):
            raise InvalidAPIUsage("(POST) missed required key(-s)", status_code=404)
        
    query = (model
        .insert(**fields)
        # .execute()
    )
    return query


def _put_query(model):
    fields = _get_fields(fields_mapping[model]["all"])
    required_field = fields_mapping[model]["pk"]
    if required_field not in fields:
        raise InvalidAPIUsage(f"(PUT) missed key: '{required_field}'", status_code=404)

    value = fields.pop(required_field)
    query = (model
        .update(**fields)
        .where(model._meta.get_primary_keys()[0] == value)
        # .execute()
    )
    return query


def _delete_query(model):
    fields = _get_fields(fields_mapping[model]["all"])
    required_field = fields_mapping[model]["pk"]
    if required_field not in fields:
        raise InvalidAPIUsage(f"(DELETE) missed key: '{required_field}'", status_code=404)

    value = fields.pop(required_field)
    query = (model
        .delete()
        .where(model._meta.get_primary_keys()[0] == value)
        # .execute()
    )
    return query


def create_response(query):
    def _prepare(obj):
        # print(type(obj), type(obj[0]), obj)
        if isinstance(obj[0], (dt.time, dt.date)):
            return list(map(lambda x: x.isoformat() if x is not None else x, obj))
        else:
            return obj
    
    def _handle_cursor(cursor):
        cols = [desc[0] for desc in cursor.description]
        if cursor.rowcount:
            output = cursor.fetchmany()[0]
            result = { cols[i]: [output[i], ] for i in range(len(output)) }
        else:
            result = None
        return result

    response = { "result": None, "ok": True }
    if request.method == 'GET':
        if isinstance(query, type(g.db_link.cursor())):
            response["result"] = _handle_cursor(query)
        else:
            temp = [row.__data__ for row in query]
            if temp:
                response["result"] = { x: [y[x] for y in temp] for x in temp[0] }
                for key in response["result"]:
                    response["result"][key] = _prepare(response["result"][key])
    return make_response(jsonify(response))


def get_aircrafts_query():
    args = dict(request.args)
    
    query = Aircraft.select()
    if "tail-no" in args:
        query = query.where(Aircraft.tail_no == args["tail-no"])
    if "mfr" in args:
        query = query.where(Aircraft.mfr == args["mfr"])
    if "model" in args:
        query = query.where(Aircraft.model.contains(args["mfr"]))
    if "younger" in args:
        query = query.where(Aircraft.bday >= dt.datetime.strptime(args["younger"], '%Y-%m-%d').date())
    if "older" in args:
        query = query.where(Aircraft.bday <= dt.datetime.strptime(args["older"], '%Y-%m-%d').date())

    limit = request.args.get("limit") or DEFAULT_BULKSIZE
    query = query.limit(limit)

    return create_response(query)


def modify_aircrafts_query():
    query = None

    if request.method == 'POST':
        query = _post_query(Aircraft)
    if request.method == 'PUT':
        query = _put_query(Aircraft)
    if request.method == 'DELETE':
        query = _delete_query(Aircraft)

    return create_response(query)


def get_airports_query():
    args = dict(request.args)

    query = Airport.select()
    if "iata" in args:
        query = query.where(Airport.iata == args["iata"])
    if "city" in args:
        query = query.where(Airport.city == args["city"])
    if "state" in args:
        query = query.where(Airport.state == args["state"])
    if "country" in args:
        query = query.where(Airport.country == args["country"])

    limit = request.args.get("limit") or DEFAULT_BULKSIZE
    query = query.limit(limit)

    return create_response(query)


def modify_airports_query():
    query = None

    if request.method == 'POST':
        query = _post_query(Airport)
    if request.method == 'PUT':
        query = _put_query(Airport)
    if request.method == 'DELETE':
        query = _delete_query(Airport)

    return create_response(query)


def get_airlines_query():
    args = dict(request.args)
    
    query = Airline.select()
    if "id" in args:
        query = query.where(Airline.airline_id == args["id"])

    limit = request.args.get("limit") or DEFAULT_BULKSIZE
    query = query.limit(limit)

    return create_response(query)


def modify_airlines_query():
    query = None

    if request.method == 'POST':
        query = _post_query(Airline)
    if request.method == 'PUT':
        query = _put_query(Airline)
    if request.method == 'DELETE':
        query = _delete_query(Airline)

    return create_response(query)


def get_flights_query():
    args = dict(request.args)
    
    query = Flight.select()
    if "id" in args:
        query = query.where(Flight.id == args["id"])
    if "flightid" in args:
        aid, fid = args["flightid"][:2], args["flightid"][2:]
        query = query.where(Flight.airline_id == aid).where(Flight.flight_id == fid)
    if "date" in args:
        query = query.where(Flight.flight_date == dt.datetime.strptime(args["date"], '%Y-%m-%d').date())
    if "dow" in args:
        query = query.where(Flight.day_of_week == args["dow"])
    if "tail-no" in args:
        query = query.where(Flight.tail_no == args["tail-no"])
    if "from" in args:
        query = query.where(Flight.origin == args["from"])
    if "to" in args:
        query = query.where(Flight.dest == args["to"])

    limit = request.args.get("limit") or DEFAULT_BULKSIZE
    query = query.limit(limit)

    return create_response(query)


def modify_flights_query():
    query = None

    if request.method == 'POST':
        query = _post_query(Flight)
    if request.method == 'PUT':
        query = _put_query(Flight)
    if request.method == 'DELETE':
        query = _delete_query(Flight)
    
    return create_response(query)


def get_ac_operator_query():
    tail_no = request.args.get("tail-no") or "N81449"

    cursor = g.db_link.cursor()
    cursor.execute(f"SELECT * FROM get_ac_operator('{tail_no}');")
    return create_response(cursor)


def get_avgtime_query():
    aid = request.args.get("id") or "DL"
    # FlightAlias = Flight.alias()
    # subquery = (FlightAlias
    #     .select(
    #         FlightAlias.airline_id,
    #         orm.SQL("((extract(hour from scheduled_time)::INT * 60) + extract(minute from scheduled_time)::INT) as scheduled"),
    #         orm.SQL("((extract(hour from real_time)::INT * 60) + extract(minute from real_time)::INT) as actual")
    #     )
    #     .where(FlightAlias.airline_id == aid)
    #     .limit(2)
    #     .alias("parsed")
    # )
    # query = (Flight
    #     .select(
    #         subquery.c.airline_id,
    #         orm.fn.AVG(subquery.c.scheduled).over(partition_by=[subquery.c.airline_id]).alias("AVG_scheduled"),
    #         orm.fn.AVG(subquery.c.actual).over(partition_by=[subquery.c.airline_id]).alias("AVG_actual")
    #     )
    #     .from_(subquery)
    # )
    # query = (Flight
    #     .select(
    #         Flight.airline_id,
    #         Flight.raw("(extract(hour from scheduled_time)::INT * 60) + extract(minute from scheduled_time)::INT as scheduled"),
    #         orm.SQL("((extract(hour from real_time)::INT * 60) + extract(minute from real_time)::INT) as actual")
    #     )
    #     .limit(5)
    cursor = g.db_link.cursor()
    cursor.execute(f"\
        SELECT DISTINCT\n\
            tmpq.airline_id,\n\
            tmpq.fullname,\n\
            (AVG(tmpq.scheduled) OVER(PARTITION BY tmpq.airline_id))::NUMERIC(5,2) AS \"AVG scheduled\",\n\
            (AVG(tmpq.actual) OVER(PARTITION BY tmpq.airline_id))::NUMERIC(5,2) AS \"AVG actual\"\n\
        FROM (\n\
            SELECT\n\
                d.airline_id,\n\
                al.fullname,\n\
                ((extract(hour from d.scheduled_time)::INT * 60) + extract(minute from d.scheduled_time)::INT) AS scheduled,\n\
                ((extract(hour from d.real_time)::INT * 60) + extract(minute from d.real_time)::INT) AS actual\n\
            FROM\n\
                delays d JOIN airlines al\n\
                ON d.airline_id = al.airline_id\n\
            WHERE al.airline_id = '{aid}'\n\
        ) tmpq;\
    ")

    return create_response(cursor)
