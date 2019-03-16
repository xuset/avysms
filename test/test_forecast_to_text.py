import json
import unittest

from test.utils import read_file
from forecast import Forecast
from forecast_to_text import forecast_to_text, MAX_SEGMENTS, MAX_SGEMENT_CHARS


class TestForecastToText(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_forecast_to_text(self):
        forecast = Forecast.from_json(read_file('./test/fixtures/sangre.json'))
        actual_text = forecast_to_text(forecast, long=True)
        self.assertEqual(1, len(actual_text))
        expected_text = read_file('./test/fixtures/sangre.txt').strip()
        self.assertEqual(expected_text, actual_text[0].strip())

    def test_forecast_to_text__large_forecast__is_shortened(self):
        forecast = Forecast(description="a" * 2000)
        text = forecast_to_text(forecast, long=True)
        self.assertEqual(1, len(text))
        self.assertEqual(MAX_SEGMENTS * MAX_SGEMENT_CHARS, len(text[0]))
