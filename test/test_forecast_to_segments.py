import jsonpickle
import unittest

from test.utils import read_file
from forecast import Forecast
from forecast_to_segments import forecast_to_segments


class TestForecastToSegments(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_forecast_to_segments(self):
        forecast = Forecast.from_json(read_file('./test/fixtures/sangre.json'))
        actual_segments = forecast_to_segments(forecast)
        expected_segments = jsonpickle.decode(
            read_file('./test/fixtures/sangre.segments.json'))

        self.assertEqual(
            jsonpickle.encode(expected_segments),
            jsonpickle.encode(actual_segments))

        self.assertEqual(
            jsonpickle.encode(expected_segments),
            jsonpickle.encode(actual_segments))
