#! /usr/bin/env python3

import argparse
import os

import boto3
import botocore

from email import policy
from email.parser import BytesParser
from email.message import EmailMessage

from interpreter import interpret
from utils import logger

LOG = logger(__name__)
EMAIL_S3_BUCKET_NAME = 'avysms-email'
FORECAST_EMAIL_ADDRESS = "AVYSMS Forecast<forecast@avysms.com>"


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


def get_email_body(parsed_email):
    return parsed_email.get_body(preferencelist='plain').get_content()


def send_email(email_to_send):
    to = email_to_send['To']
    LOG.info('event=sending_email, to=%s', to)

    response = boto3.client('ses').send_raw_email(
        RawMessage={
            'Data': email_to_send.as_bytes()
        }
    )

    LOG.info('event=sent_email, to=%s, ses_message_id=%s', to, response['MessageId'])


def create_email_reference_list(request_email):
    references = request_email.get('References', '').split(' ')

    if 'Message-ID' in request_email:
        references.append(request_email['Message-ID'])

    references = list(filter(lambda ref: len(ref.strip()) > 0, references))

    return ' '.join(references) if len(references) > 0 else None


def create_response_email(request_email, response_body):
    response_email = EmailMessage()
    response_email['To'] = request_email['From']
    response_email['From'] = FORECAST_EMAIL_ADDRESS
    response_email['Subject'] = 'Re: ' + request_email['Subject']
    response_email['References'] = create_email_reference_list(request_email)
    response_email.set_content(response_body)
    return response_email


def email_handler(event, should_reply=True):
    LOG.info('event=email_handler_invoked, event=%s', event)

    ses_mail = event["Records"][0]["ses"]["mail"]
    from_address = ses_mail.get("source")
    ses_message_id = ses_mail["messageId"]

    request_email = retreive_email_from_s3(ses_message_id)
    request_body = get_email_body(request_email)

    response_body = "\n\n".join(interpret(request_body))
    response_email = create_response_email(request_email, response_body)

    if should_reply:
        send_email(response_email)

    LOG.info('event=email_handler_success')

    return response_email


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
