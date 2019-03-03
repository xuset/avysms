#! /usr/bin/env python3

import boto3
import sys
import datetime
import os

from download_caic_html import download_html
from utils import safe, logger

FORECAST_REGION = 'CAIC'
ZONE_IDS = range(0, 10)
BUCKET_NAME = 'avysms-forecast'
S3 = boto3.resource('s3')
LOG = logger(__name__)


@safe(log=LOG)
def cache_html(zone_id):
    object_name = os.path.join(FORECAST_REGION, str(zone_id), str(datetime.datetime.now()))
    LOG.info("event=caching_invoked, object_name=%s", object_name)
    html = download_html(zone_id)
    object = S3.Object(BUCKET_NAME, object_name)
    object.put(Body=html)
    LOG.info("event=caching_success, object_name=%s", object_name)
    return html


def update_cache():
    return list(map(cache_html, ZONE_IDS))


def lambda_handler(event, context):
    LOG.info("event=lambda_invoked, lambda_event=%s, lambda_context=%s", event, context)
    update_cache()
    LOG.info("event=lambda_success")


if __name__ == "__main__":
    lambda_handler(None, None)
