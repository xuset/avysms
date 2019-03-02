#! /usr/bin/env python3

import argparse
import json
import requests
import sys

def download_html(zone_id):
  url = "https://avalanche.state.co.us/caic/pub_bc_avo.php?zone_id={}".format(zone_id)
  response = requests.get(url)
  response.raise_for_status()
  return response.text

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("-z", "--zone-id", type=int, default=9)
  args = parser.parse_args()
  print("Downloading forecast for zone_id={}".format(args.zone_id), file=sys.stderr)
  sys.stdout.write(download_html(args.zone_id))
