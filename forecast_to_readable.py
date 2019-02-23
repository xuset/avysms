import sys
import json

from forecast import Forecast

def is_not_None(obj):
  return obj is not None

def convert_forecast_to_human_readable_text(forecast):
  return '\n\n'.join(filter(is_not_None, [
    forecast.date,
    forecast.description
  ]))

if __name__ == "__main__":
  forecast = Forecast(**json.load(sys.stdin))
  print(convert_forecast_to_human_readable_text(forecast))
  
  
