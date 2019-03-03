import logging
import sys


def logger(name):
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(name)s] - %(levelname)s - %(message)s",
        datefmt="%m-%d-%YT%H:%M:%S%z",
        stream=sys.stderr)
    return logging.getLogger(name)


LOG = logger(__name__)


def is_not_None(obj):
    return obj is not None


def safe(safe_return_value=None, log=LOG):
    def wrap(function):
        def internal(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as e:
                log.exception(e)
            return safe_return_value
        return internal
    return wrap
