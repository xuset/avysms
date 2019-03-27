#! /usr/bin/env python3

import argparse

from utils import logger, requests_session

LOG = logger(__name__)


def download_html(zone_id):
    url = "https://avalanche.state.co.us/caic/pub_bc_avo.php?zone_id={}".format(zone_id)
    LOG.info('event=downloading_forecast, url=%s', url)
    response = requests_session().get(url)
    response.raise_for_status()
    return response.text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-z", "--zone-id", type=int, default=9)
    args = parser.parse_args()
    print(download_html(args.zone_id))
