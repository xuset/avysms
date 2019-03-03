#! /usr/bin/env python3

import json
import sys

from text_interface import do_command
from utils import logger

LOG = logger(__name__)


def lambda_handler(event, context):
    LOG.info('event=lambda_invoked, lambda_event=%s, lambda_context=%s', event, context)
    request_body = event["queryStringParameters"]["Body"]
    result = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/plain"
        },
        "body": do_command(request_body)
    }
    LOG.info('event=lambda_return, result=%s', result)
    return result


if __name__ == "__main__":
    event = {
        "queryStringParameters": {
            "Body": " ".join(sys.argv[1:])
        }
    }
    json.dump(lambda_handler(event, None), sys.stdout)
