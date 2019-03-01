import sys

from forecast import Zone
from utils import safe
from download_caic_forecast import download_html
from caic_html_to_forecast import parse_forecast
from forecast_to_readable import convert_forecast_to_human_readable_text


CAIC_ZONES_IDS = {
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

CAIC_ZONES_IDS_TO_ZONES = {
  0: Zone.Steamboat,
  1: Zone.FrontRange,
  2: Zone.Vail,
  3: Zone.Sawatch,
  4: Zone.Aspen,
  5: Zone.Gunnison,
  6: Zone.GrandMesa,
  7: Zone.NorthSanJuan,
  8: Zone.SouthSanJuan,
  9: Zone.SangreDeCristo
}

HELP_TEXT = "\n".join([
"This is an automated avalanche forecast service for Colorado.",
"Reply with one of the available regions to receive the latest forecast:",
"",
] + list(CAIC_ZONES_IDS.keys()))

@safe(safe_return_value=HELP_TEXT)
def do_command(text):
  text = text.split(' ')[0]
  for zone_name, zone_id in CAIC_ZONES_IDS.items():
    if zone_name.lower().startswith(text.lower()):
      zone = CAIC_ZONES_IDS_TO_ZONES.get(zone_id, None)
      html = download_html(zone_id)
      forecast = parse_forecast(html, zone)
      return convert_forecast_to_human_readable_text(forecast)
  return HELP_TEXT

if __name__ == "__main__":
  print(do_command(" ".join(sys.argv[1:])))
