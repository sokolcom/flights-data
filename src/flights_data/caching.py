import hashlib
import redis

from flask import request, make_response, jsonify
import json


r = redis.Redis(host='localhost', port=6379)


LRU_CACHE = "hot"
HLRU_CACHE = "h:hot"
LRU_SIZE = 10

WARM_CACHE = "warm"
HWARM_CACHE = "h:warm"
WARM_SIZE = 20


def cache(func):
    def _serialize(json_string):
        obj = json.loads(json_string)
        if obj is None:
            obj = None
        return obj

    def _in_cache(element, cache):
        return element in r.lrange(cache, 0, -1)

    def _clean_htable(cache, table):
        elements = None
        hkeys = None
        with r.pipeline(transaction=True) as pipe:
            pipe.multi()
            pipe.lrange(cache, 0, -1)
            pipe.hkeys(table)
            elements, hkeys = pipe.execute()
            to_delete = list(filter(lambda x: x not in elements, hkeys))  or ["stub"]

            pipe.multi()
            pipe.hdel(table, *to_delete)
            pipe.execute()

    def wrapper():
        if request.method != "GET":
            return func()
        
        hashed_query = hashlib.sha256(request.full_path.encode(encoding="utf-8")).digest()
        response = None

        with r.pipeline(transaction=True) as pipe:
            # If in the LRU cache
            if _in_cache(hashed_query, LRU_CACHE):
                pipe.multi()
                pipe.lrem(LRU_CACHE, 1, hashed_query)
                pipe.lpush(LRU_CACHE, hashed_query)
                pipe.ltrim(LRU_CACHE, 0, LRU_SIZE - 1)
                _clean_htable(LRU_CACHE, HLRU_CACHE)
                pipe.hget(HLRU_CACHE, hashed_query)
                result = pipe.execute()[3]
                response = make_response(jsonify({ "ok": True, 'result': _serialize(result.decode()) }))
            # If in the WARM QUEUE
            elif _in_cache(hashed_query, WARM_CACHE):
                pipe.multi()
                pipe.lrem(WARM_CACHE, 1, hashed_query)
                pipe.lpush(LRU_CACHE, hashed_query)
                pipe.ltrim(LRU_CACHE, 0, LRU_SIZE - 1)
                _clean_htable(LRU_CACHE, HLRU_CACHE)
                pipe.hget(HWARM_CACHE, hashed_query)
                result = pipe.execute()[3]
                response = make_response(jsonify({ "ok": True, 'result': _serialize(result.decode()) }))

                pipe.multi()
                pipe.hdel(HWARM_CACHE, hashed_query)
                pipe.hset(HLRU_CACHE, hashed_query, result)
                pipe.execute()
            # First ocasion
            else:
                pipe.multi()
                pipe.lpush(WARM_CACHE, hashed_query)
                pipe.ltrim(WARM_CACHE, 0, WARM_SIZE - 1)
                _clean_htable(WARM_CACHE, HWARM_CACHE)
                response = func()
                temp = json.loads(response.response[0].decode())["result"]
                pipe.hset(HWARM_CACHE, hashed_query, json.dumps(temp).encode())
                pipe.execute()
            
        return response

    wrapper.__name__ = func.__name__
    return wrapper
