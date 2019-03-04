# [AVYSMS.COM](http://www.avysms.com/)

##### Automated text message service for retrieving avalanche forecasts

This repo is the code for the backend of avysms.com. It provides the ability to download Colorado Avalanche Information Center (CAIC) webpages, parse them, and convert them to human readable text so that it can be sent via sms.

## Setup

Setup the python3 virtual environment and install dependencies

`make install`

Activate the virtual environment

`source ./venv/bin/activate`

Run the tests

`make test`

## Usage

#### `download_caic_html.py [-z ZONE_ID]`
Downloads the html for the CIAC forecast for the given region

#### `caic_html_to_forecast.py`
Parsers the html forecast into an intermediary data structure represented as json

#### `forecast_to_text.py`
Converts the intermediary json data structure to human readable forecast_to_text

## Example

#### Chaining it all together:

`./download_caic_html.py -z 0 | ./caic_html_to_forecast.py | ./forecast_to_text.py`

This downloads the latest forecast for the Steamboat (zone 0) region and converts it to a human readable text response

#### Using the SMS interface

The SMS text interface uses the same flow as described above, downloading the forecast and converting it to human readable text. This interfaces supports additional commands like specifying regions by their name. Its this interface that handles interpreting the sms requests and sending the appropriate sms response.

`text_interface.py [sms message body]`

`./text_interface.py front range`
