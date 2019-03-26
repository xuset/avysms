#! /usr/bin/env python3

import re

from bs4 import BeautifulSoup
from urllib.parse import unquote

from utils import safe, logger, Data, requests_session


class InReachResponse(Data):
    def __init__(self, reply_url, guid, reply_address, response_segments):
        self.reply_url = reply_url
        self.guid = guid
        self.reply_address = reply_address
        self.response_segments = response_segments


LOG = logger(__name__)

INREACH_REPLY_URL_REGEX = re.compile(r"http.*inreach.*textmessage/txtmsg")

GUID_GROUP_REGEX = re.compile(r"extId=([a-zA-Z0-9-]+)")

REPLY_ADDRESS_REGEX = re.compile(r"adr=([^&]+)")

BASE_URL_REGEX = re.compile(r"^https?://[^?]+")


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

    return reply_url_root.get('href', None) if reply_url_root is not None else None


def create_inreach_response(request_email, response_segments):
    reply_url = extract_reply_url_from_request_email(request_email)
    guid = extract_guuid_from_reply_url(reply_url)
    reply_address = extract_reply_address_from_reply_url(reply_url)

    response = InReachResponse(reply_url, guid, reply_address, response_segments)
    LOG.info('event=created_increach_response, response=%s', response)
    return response


@safe(safe_return_value=False, log=LOG)
def is_inreach_response_successful(response):
    return response.json()['Success'] is True


@safe(log=LOG)
def send_inreach_response_segment(base_url, reply_address, guid, response_segment):
    payload = {
        "ReplyAddress": reply_address,
        "ReplyMessage": response_segment,
        "Guid": guid
    }
    LOG.info('event=sending_inreach_response_segment, base_url=%s, payload=%s', base_url, payload)

    response = requests_session().post(base_url, data=payload)

    if is_inreach_response_successful(response):
        LOG.info('event=sent_inreach_response_segment')
    else:
        response_str = " ".join([str(response.status_code), response.reason, response.text])
        LOG.error('event=send_inreach_response_segment_failed, response=%s', response_str)


def send_inreach_response(inreach_response):
    base_url = extract_base_url_from_reply_url(inreach_response.reply_url)

    for response_segment in inreach_response.response_segments:
        send_inreach_response_segment(**{
            "base_url": base_url,
            "reply_address": inreach_response.reply_address,
            "guid": inreach_response.guid,
            "response_segment": response_segment
        })

    LOG.info('event=sent_inreach_response')


@safe(safe_return_value=False, log=LOG)
def is_request_email_from_inreach(request_email):
    return extract_reply_url_from_request_email(request_email) is not None
