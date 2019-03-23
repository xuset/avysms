#! /usr/bin/env python3

import argparse
import sys

from forecast import Zone
from utils import safe, logger
from download_caic_html import download_html
from caic_html_to_forecast import parse_forecast
from forecast_to_segments import forecast_to_segments
from format_segments import format_segments

LOG = logger(__name__)

CAIC_ZONE_NAMES = [
    "Steamboat & Flat Tops",
    "Front Range",
    "Vail & Summit County",
    "Sawatch",
    "Aspen",
    "Gunnison",
    "Grand Mesa",
    "North San Juan",
    "South San Juan",
    "Sangre de Cristo"
]

CAIC_ZONE_MATCHES_TO_IDS = [
    ("steam", 0),
    ("flat", 0),
    ("front", 1),
    ("vail", 2),
    ("summit", 2),
    ("sawatch", 3),
    ("aspen", 4),
    ("gunnison", 5),
    ("grand mesa", 6),
    ("mesa", 6),
    ("north san juan", 7),
    ("north juan", 7),
    ("south san juan", 8),
    ("south juan", 8),
    ("san juan", 7),  # Default to North San Juan if north/south not specifie
    ("juan", 7),  # Default to North San Juan if north/south not specifie
    ("sangre", 9)
]


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
    "This is an automated service for avalanche forecasts.",
    "Reply with one of the available regions to receive the latest forecast.",
    "",
    *CAIC_ZONE_NAMES,
])


@safe(safe_return_value=[HELP_TEXT], log=LOG)
def interpret(request, joined):
    request = request.lower()

    for zone_name, zone_id in CAIC_ZONE_MATCHES_TO_IDS:
        if request.startswith(zone_name):
            zone = CAIC_ZONES_IDS_TO_ZONES.get(zone_id, None)
            html = download_html(zone_id)
            forecast = parse_forecast(html, zone)
            segments = forecast_to_segments(forecast)
            return format_segments(segments, joined)

    LOG.warning("event=unknown_request, request=%s", request)
    return [HELP_TEXT]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("request", nargs='*')
    args = parser.parse_args()

    if len(args.request) > 0:
        request = " ".join(args.request)
        print("\n\n".join(interpret(request, joined=True)))
    else:
        print(" > ", end="", flush=True)
        for line in sys.stdin:
            print("\n\n".join(interpret(line, joined=True)))
            print("\n > ", end="", flush=True)
