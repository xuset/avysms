import sys
import json
from bs4 import BeautifulSoup

from forecast import Forecast
from utils import safe_eval

def find_forecast_description(root):
  return root.find_all("div", attrs={"class": "fx-text-area"})[0].find("p").string

def parse_forecast(html):
  soup = BeautifulSoup(html, 'html.parser')
  root = soup.find(id="avalanche-forecast")

  description = safe_eval(find_forecast_description, root)

  return Forecast(description)

if __name__ == "__main__":
  json.dump(parse_forecast(sys.stdin).to_dict(), sys.stdout)
