#! /usr/bin/env python3

import argparse
import os
from email import policy
from email.parser import BytesParser

import boto3
import botocore

from inreach import is_request_email_from_inreach, send_inreach_response, create_inreach_response
from interpreter import interpret
from utils import logger

LOG = logger(__name__)
EMAIL_S3_BUCKET_NAME = 'avysms-email'


def retreive_email_from_s3(ses_message_id):
    s3 = boto3.resource('s3')
    try:
        key = os.path.join('received', ses_message_id)
        raw_bytes = s3.Object(EMAIL_S3_BUCKET_NAME, key).get()['Body'].read()
        return BytesParser(policy=policy.default).parsebytes(raw_bytes)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            LOG.error('event=email_not_found, ses_message_id=%s', ses_message_id)
        raise e


def email_handler(event, should_reply=True):
    LOG.info('event=email_handler_invoked, event=%s', event)

    ses_message_id = event["Records"][0]["ses"]["mail"]["messageId"]

    request_email = retreive_email_from_s3(ses_message_id)
    request_body = request_email.get_body(preferencelist='plain').get_content()

    if not is_request_email_from_inreach(request_email):
        LOG.warning('event=email_not_from_inreach, from=%s', request_email['From'])
        return

    response_segments = interpret(request_body, joined=False)
    inreach_response = create_inreach_response(request_email, response_segments)
    if should_reply:
        send_inreach_response(inreach_response)

    LOG.info('event=email_handler_success, body=%s', response_segments)

    return inreach_response


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--ses-message-id", required=True)
    parser.add_argument("-r", "--reply", action='store_true')
    args = parser.parse_args()

    event = {
        "Records": [
            {
                "ses": {
                    "mail": {
                        "messageId": args.ses_message_id
                    }
                }
            }
        ]
    }

    print(str(email_handler(event, args.reply)))
