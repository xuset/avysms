import atexit
import json
import jsonpickle
import logging
import requests
import sys
import traceback


def logger(name):
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s %(levelname)s %(name)s] %(message)s",
        datefmt="%m-%d-%YT%H:%M:%S%z",
        stream=sys.stderr)
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)
    return log


LOG = logger(__name__)

REQUESTS_SESSION = None


def close_requests_session():
    global REQUESTS_SESSION
    if REQUESTS_SESSION is not None:
        REQUESTS_SESSION.close()
        REQUESTS_SESSION = None


def requests_session():
    global REQUESTS_SESSION
    if REQUESTS_SESSION is None:
        atexit.register(close_requests_session)
        REQUESTS_SESSION = requests.Session()
        REQUESTS_SESSION.headers.update({
            'User-Agent': 'avysms.com 1.0'
        })
    return REQUESTS_SESSION


def is_not_None(obj):
    return obj is not None


def safe(safe_return_value=None, log=LOG):
    def wrap(function):
        def internal(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as e:
                tb = traceback.format_exc().replace('\n', '->')
                log.error('event=safe_handling, message=%s, traceback=%s', str(e), tb)
            return safe_return_value
        return internal
    return wrap


class Data(object):
    def __str__(self):
        return str(dict(self))

    def __iter__(self):
        return iter(json.loads(jsonpickle.encode(self, unpicklable=False)).items())

    def to_json(self):
        return jsonpickle.encode(self)

    @staticmethod
    def from_json(json_str):
        return jsonpickle.decode(json_str if not hasattr(json_str, 'read') else json_str.read())
