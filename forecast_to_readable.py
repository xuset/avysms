import sys
import json

from forecast import Forecast

def convert_forecast_to_human_readable_text(forecast):
  return forecast.description

if __name__ == "__main__":
  forecast = Forecast.from_dict(json.load(sys.stdin))
  print(convert_forecast_to_human_readable_text(forecast))
  
  
