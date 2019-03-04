#! /usr/bin/env python3

import sys

from forecast import Zone
from utils import safe, logger
from download_caic_html import download_html
from caic_html_to_forecast import parse_forecast
from forecast_to_text import forecast_to_text

LOG = logger(__name__)

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
    "This is an automated text message service for retrieving avalanche forecasts",
    "",
    "Available regions:",
    *CAIC_ZONES_IDS.keys(),
    "",
    "Reply with one of the available regions to receive the latest forecast.",
    "Add the word 'short' to receive a shortened variation"
])


@safe(safe_return_value=[HELP_TEXT], log=LOG)
def do_command(request):
    short = 'short' in request
    request_region = request.split(' ')[0]
    for zone_name, zone_id in CAIC_ZONES_IDS.items():
        if zone_name.lower().startswith(request_region.lower()):
            zone = CAIC_ZONES_IDS_TO_ZONES.get(zone_id, None)
            html = download_html(zone_id)
            forecast = parse_forecast(html, zone)
            return forecast_to_text(forecast, short=short, segmented=short)
    LOG.warning("event=unknown_request, request=%s", request)
    return [HELP_TEXT]


if __name__ == "__main__":
    print("\n\n".join(do_command(" ".join(sys.argv[1:]))))
