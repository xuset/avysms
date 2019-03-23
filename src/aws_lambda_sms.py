#! /usr/bin/env python3

import json
import sys
import os

from twilio.twiml.messaging_response import Message, MessagingResponse

from interpreter import interpret
from utils import logger, safe

LOG = logger(__name__)


@safe(safe_return_value="Error retrieving forecast", log=LOG)
def messages_to_twiml(messages):
    messages = [messages] if isinstance(messages, str) else messages
    response = MessagingResponse()
    for msg in messages:
        response.message(msg)
    return response


def sms_handler(event):
    LOG.info('event=sms_handler_invoked, event=%s', event)

    # from_number = event["queryStringParameters"].get("From", None)
    body = event["queryStringParameters"]["Body"]

    result = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/xml"
        },
        "body": str(messages_to_twiml(interpret(body, joined=False)))
    }

    LOG.info('event=sms_handler_success, result=%s', result)
    return result


if __name__ == "__main__":
    event = {
        "queryStringParameters": {
            "Body": " ".join(sys.argv[1:])
        }
    }
    json.dump(sms_handler(event), sys.stdout)
