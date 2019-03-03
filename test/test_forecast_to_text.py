import json
import unittest

from test.utils import read_file
from forecast import Forecast
from forecast_to_text import convert_forecast_to_text


class TestForecastToText(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_convert_forecast_to_text(self):
        forecast = Forecast.from_json(read_file('./test/fixtures/sangre.json'))
        actual_text = convert_forecast_to_text(forecast)
        expected_text = read_file('./test/fixtures/sangre.txt')
        self.assertEqual(expected_text, actual_text)
