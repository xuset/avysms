import sys

from utils import safe_eval
from download_caic_forecast import retrieve_forecast
from forecast_to_readable import convert_forecast_to_human_readable_text


CAIC_ZONES = {
  "Steamboat & Flat Tops": 0,
  "Front Range": 1,
  "Vail & Summit County": 2,
  "Sawatch": 3,
  "Aspen": 4,
  "Gunnison": 5,
  "Grand Mesa": 6,
  "North San Juan": 7,
  "South San Juan": 8,
  "Sangre de Cristo": 9
}

HELP_TEXT = "\n".join([
"This is an automated avalanche forecast service for Colorado.",
"Reply with one of the available regions to receive the latest forecast:",
"",
] + list(CAIC_ZONES.keys()))

def do_forecast(text):
  text = text.split(' ')[0]
  for zone_name, zone_id in CAIC_ZONES.items():
    if zone_name.lower().startswith(text.lower()):
      forecast = retrieve_forecast(zone_id)
      return convert_forecast_to_human_readable_text(forecast)
  return HELP_TEXT


def do_command(text):
  return safe_eval(do_forecast, text, safe_return_value=HELP_TEXT)

if __name__ == "__main__":
  print(do_command(" ".join(sys.argv[1:])))
