#! /usr/bin/env python3

import re

from bs4 import BeautifulSoup
from urllib.parse import unquote

from utils import safe, logger, Data, requests_session


class InReachResponse(Data):
    def __init__(self, reply_url, guid, message_id, reply_address, response_segments):
        self.reply_url = reply_url
        self.guid = guid
        self.message_id = message_id
        self.reply_address = reply_address
        self.response_segments = response_segments


LOG = logger(__name__)

INREACH_REPLY_URL_REGEX = re.compile(r"http.*inreach.*textmessage/txtmsg")

GUID_GROUP_REGEX = re.compile(r"extId=([a-zA-Z0-9-]+)")

REPLY_ADDRESS_REGEX = re.compile(r"adr=([^&]+)")

# TODO Wrong
BASE_URL_REGEX = re.compile(r"^https?://[^?]+")


def retreive_message_id(reply_url):
    response = requests_session().get(reply_url)
    response.raise_for_status()
    html_root = BeautifulSoup(response.text, 'html.parser')
    message_id_root = html_root.find("input", id="MessageId")
    message_id = message_id_root['value']
    return message_id


def extract_guuid_from_reply_url(reply_url):
    groups = GUID_GROUP_REGEX.search(reply_url)
    guid = groups.group(1)
    return guid


def extract_base_url_from_reply_url(reply_url):
    base_url = BASE_URL_REGEX.search(reply_url).group(0)
    return base_url


def extract_reply_address_from_reply_url(reply_url):
    reply_address = unquote(REPLY_ADDRESS_REGEX.search(reply_url).group(1))
    return reply_address


def extract_reply_url_from_request_email(request_email):
    html_text = request_email.get_body(preferencelist='html').get_content()
    html_root = BeautifulSoup(html_text, 'html.parser')
    reply_url_root = html_root.find("a", href=INREACH_REPLY_URL_REGEX)

    if reply_url_root is None:
        return None
    reply_url = reply_url_root.get('href', None)

    return reply_url


def create_inreach_response(request_email, response_segments):
    reply_url = extract_reply_url_from_request_email(request_email)
    guid = extract_guuid_from_reply_url(reply_url)
    message_id = retreive_message_id(reply_url)
    reply_address = extract_reply_address_from_reply_url(reply_url)

    response = InReachResponse(reply_url, guid, message_id, reply_address, response_segments)
    LOG.info('event=created_increach_response, response=%s', response)
    return response


@safe(log=LOG)
def send_inreach_response_segment(base_url, reply_address, message_id, guid, response_segment):
    payload = {
        "ReplyAddress": reply_address,
        "ReplyMessage": response_segment,
        "MessageId": message_id,
        "Guid": guid
    }
    LOG.info('event=sending_inreach_response_segment, base_url=%s, payload=%s', base_url, payload)
    response = requests_session().post(base_url, data=payload)
    response.raise_for_status()
    success = response.json()["Success"] is True
    LOG.info('event=sent_inreach_response_segment, success=%s', success)


def send_inreach_response(inreach_response):
    base_url = extract_base_url_from_reply_url(inreach_response.reply_url)
    for response_segment in inreach_response.response_segments:
        send_inreach_response_segment(**{
            "base_url": base_url,
            "reply_address": inreach_response.reply_address,
            "message_id": inreach_response.message_id,
            "guid": inreach_response.guid,
            "response_segment": response_segment
        })

    LOG.info('event=sent_inreach_response')


@safe(safe_return_value=False, log=LOG)
def is_request_email_from_inreach(request_email):
    return extract_reply_url_from_request_email(request_email) is not None
