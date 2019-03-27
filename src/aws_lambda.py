#! /usr/bin/env python3

import json
import sys

from aws_lambda_email import email_handler
from aws_lambda_sms import sms_handler
from utils import logger

LOG = logger(__name__)


def entrypoint(event, context):
    if "queryStringParameters" in event:
        return sms_handler(event)
    elif event.get("Records", [{}])[0].get("eventSource") == "aws:ses":
        email_handler(event)  # Don't return anything for ses events
    else:
        LOG.error('event=unknown_lambda_event, event=%s', event)
        raise Exception("Unknown lambda event")


if __name__ == "__main__":
    event = {
        "queryStringParameters": {
            "Body": " ".join(sys.argv[1:])
        }
    }
    json.dump(entrypoint(event, None), sys.stdout)
