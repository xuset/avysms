import sys
import json

from forecast import Forecast
from utils import is_not_None

def convert_forecast_to_human_readable_text(forecast):
  return '\n\n'.join(filter(is_not_None, [
    forecast.date,
    forecast.description
  ]))

if __name__ == "__main__":
  forecast = Forecast(**json.load(sys.stdin))
  print(convert_forecast_to_human_readable_text(forecast))
  
  
