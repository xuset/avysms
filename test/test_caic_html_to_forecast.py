import json
import unittest

from test.utils import read_file
from caic_html_to_forecast import parse_forecast
from forecast import Forecast


class TestCaicHtmlToForecast(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_parse_forecast(self):
        actual_forecast = dict(parse_forecast(read_file('./test/fixtures/sangre.html')))
        expected_forecast = dict(Forecast.from_json(read_file('./test/fixtures/sangre.json')))
        self.assertEqual(expected_forecast, actual_forecast)

    def test_parse_forecast__unknown_rating__parses_with_unknown_rating(self):
        actual_forecast = dict(parse_forecast(
            read_file('./test/fixtures/unknownrating.html')))
        expected_forecast = dict(Forecast.from_json(
            read_file('./test/fixtures/unknownrating.json')))
        self.assertEqual(expected_forecast, actual_forecast)

    def test_parse_forecast__deep_persistent_slab__parses(self):
        actual_forecast = dict(parse_forecast(
            read_file('./test/fixtures/deeppersistentslab.html')))
        expected_forecast = dict(Forecast.from_json(
            read_file('./test/fixtures/deeppersistentslab.json')))
        self.assertEqual(expected_forecast, actual_forecast)
