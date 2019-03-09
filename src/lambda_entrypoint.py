#! /usr/bin/env python3

import json
import sys

from twilio.twiml.messaging_response import Message, MessagingResponse

from text_interface import do_command
from utils import logger, safe

LOG = logger(__name__)


@safe(safe_return_value="Error retrieving forecast", log=LOG)
def messages_to_twiml(messages):
    messages = [messages] if isinstance(messages, str) else messages
    response = MessagingResponse()
    for msg in messages:
        response.message(msg)
    return response


def lambda_handler(event, context):
    LOG.info('event=lambda_invoked, lambda_event=%s, lambda_context=%s', event, context)
    request_body = event["queryStringParameters"]["Body"]
    result = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/xml"
        },
        "body": str(messages_to_twiml(do_command(request_body)))
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
