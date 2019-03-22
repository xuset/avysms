#! /usr/bin/env python3

import argparse
import json
import os
import re
import sys

import boto3
import botocore

from email import policy
from email.parser import BytesParser

from interpreter import interpret
from utils import logger, safe

LOG = logger(__name__)
EMAIL_S3_BUCKET_NAME = 'avysms-email'


def retreive_raw_email_bytes_from_s3(message_id):
    s3 = boto3.resource('s3')
    try:
        key = os.path.join('received', message_id)
        return s3.Object(EMAIL_S3_BUCKET_NAME, key).get()['Body'].read()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            LOG.error('event=email_not_found, message_id=%s', message_id)
        raise e


def strip_email_headers(body):
    # This will fail if two new line characters are expected input but this is not the case
    return re.split(r"[\n\r]{2}", body)[-1].strip()


def parse_email_body(raw_email_bytes):
    parsed_email = BytesParser(policy=policy.default).parsebytes(raw_email_bytes)
    body = str(parsed_email.get_body(preferencelist='plain'))
    body = strip_email_headers(body)
    LOG.info('event=parsed_request_body, body=%s', body)
    return body


@safe(safe_return_value="Error retreiving forecast", log=LOG)
def create_response_from_email(message_id):
    raw_email_bytes = retreive_raw_email_bytes_from_s3(message_id)
    body = parse_email_body(raw_email_bytes)

    forecast_message_segments = interpret(body)
    return "\n\n".join(forecast_message_segments)


def send_email(to, body):
    LOG.info('event=sending_email, to=%s, response_body=%s', to, body)

    if to is None:
        return

    response = boto3.client('ses').send_email(
        Destination={
            'ToAddresses': [to],
        },
        Message={
            'Body': {
                'Text': {
                    'Charset': "UTF-8",
                    'Data': body,
                },
            },
            'Subject': {
                'Charset': "UTF-8",
                'Data': "AVYSMS Avalance Forecast",
            }
        },
        Source="AVYSMS Forecast<forecast@avysms.com>"
    )

    LOG.info('event=sent_email, to=%s, message_id=%s', to, response['MessageId'])


def email_handler(event):
    LOG.info('event=email_handler_invoked, event=%s', event)

    ses_mail = event["Records"][0]["ses"]["mail"]
    from_address = ses_mail.get("source")
    message_id = ses_mail["messageId"]

    result = create_response_from_email(message_id)

    send_email(from_address, result)

    LOG.info('event=email_handler_success')

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--message-id", required=True)
    parser.add_argument("-f", "--from-address", default=None)
    args = parser.parse_args()

    event = {
        "Records": [
            {
                "ses": {
                    "mail": {
                        "messageId": args.message_id,
                        "source": args.from_address
                    }
                }
            }
        ]
    }
    json.dump(email_handler(event), sys.stdout)
