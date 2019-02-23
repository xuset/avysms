import sys
import json
from bs4 import BeautifulSoup

from forecast import Forecast
from utils import safe_eval

def find_forecast_date(root):
  return root.find_all("h2")[0].contents[0].strip()

def find_forecast_description(root):
  return root.find_all("div", attrs={"class": "fx-text-area"})[0] \
    .find("p").string.replace("\u00a0", "")

def parse_forecast(html):
  soup = BeautifulSoup(html, 'html.parser')
  root = soup.find(id="avalanche-forecast")

  date = safe_eval(find_forecast_date, root)

  description = safe_eval(find_forecast_description, root)

  return Forecast(date, description)

if __name__ == "__main__":
  json.dump(dict(parse_forecast(sys.stdin)), sys.stdout)
