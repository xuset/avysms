#! /usr/bin/env python3

import json
import sys

from aws_lambda_sms import sms_handler
from aws_lambda_email import email_handler

from utils import logger, safe


LOG = logger(__name__)


def entrypoint(event, context):
    if "queryStringParameters" in event:
        return sms_handler(event)
    elif event.get("Records", [{}])[0].get("eventSource") == "aws:ses":
        return email_handler(event)
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
