import boto3
import sys
import datetime
import os

from download_caic_forecast import download_html
from utils import safe_eval

FORECAST_REGION='CAIC'
ZONE_IDS = range(0, 10)
BUCKET_NAME = 'avysms-forecast'
S3 = boto3.resource('s3')

def cache_raw_forecast(zone_id):
  object_name = os.path.join(FORECAST_REGION, str(zone_id), str(datetime.datetime.now()))
  print("event=caching_invoked, object_name={}".format(object_name), file=sys.stderr)
  html = download_html(zone_id)
  object = S3.Object(BUCKET_NAME, object_name)
  object.put(Body=html)
  print("event=lambda_success, object_name={}".format(object_name), file=sys.stderr)

def update_cache():
  for zone_id in ZONE_IDS:
    safe_eval(cache_raw_forecast, zone_id)

def lambda_handler(event, context):
  print("event=lambda_invoked, lambda_event={}, lambda_context={}".format(event, context), file=sys.stderr)
  update_cache()
  print("event=lambda_success", file=sys.stderr)

if __name__ == "__main__":
  lambda_handler(None, None)
