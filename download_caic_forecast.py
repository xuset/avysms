import json
import requests
import sys

from caic_html_to_forecast import parse_forecast
from forecast_to_readable import convert_forecast_to_human_readable_text

def download_html(zone_id):
  url = "https://avalanche.state.co.us/caic/pub_bc_avo.php?zone_id={}".format(zone_id)
  response = requests.get(url)
  response.raise_for_status()
  return response.text

def retrieve_forecast(zone_id):
  html = download_html(zone_id)
  return parse_forecast(html)

if __name__ == "__main__":
  sangres_zone_id = 9
  sys.stdout.write(download_html(sangres_zone_id))
