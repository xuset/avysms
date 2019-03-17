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

#### `python3 src/interpreter.py`
Starts the interperter that is used to interpret incoming sms requests and generate the approrpriate forecast response

##### Example
```bash
# python3 src/interpreter.py
> front range
Front Range - Sat, Mar 16, 2019 at 7:30 AM

Avalanche dangers
  Below TL: Moderate
  Near  TL: Considerable
  Above TL: Considerable

Likely historic persistent slab avalanche problem
  Below TL: N NE E SE S SW W NW
  Near  TL: N NE E SE S SW W NW
  Above TL: N NE E SE S SW W NW

 >

```
