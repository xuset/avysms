import json
import sys

from download_caic_forecast import retrieve_forecast
from forecast_to_readable import convert_forecast_to_human_readable_text


def lambda_handler(event, context):
  sangres_zone_id = 9
  forecast = retrieve_forecast(sangres_zone_id)
  return {
    "statusCode": 200,
    "body": convert_forecast_to_human_readable_text(forecast)
  }

if __name__ == "__main__":
  json.dump(lambda_handler(None, None), sys.stdout)
  

