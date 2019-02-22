import json
import sys

from download_caic_forecast import retrieve_forecast
from forecast_to_readable import convert_forecast_to_human_readable_text

def lambda_handler(event, context):
  print('event=lambda_invoked, lambda_event={}, lambda_context={}'.format(event, context), file=sys.stderr)
  sangres_zone_id = 9
  forecast = retrieve_forecast(sangres_zone_id)
  result = {
    "statusCode": 200,
    "headers": {
      "Content-Type": "text/plain"
    },
    "body": convert_forecast_to_human_readable_text(forecast)
  }
  print('event=lambda_return, result={}'.format(result), file=sys.stderr)
  return result

if __name__ == "__main__":
  json.dump(lambda_handler(None, None), sys.stdout)
  

