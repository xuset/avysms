import json
import unittest

from test.utils import read_file
from forecast import Forecast
from format_segments import format_segments


class TestFormatSegments(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_format_segments(self):
        segments = Forecast.from_json(read_file('./test/fixtures/sangre.segments.json'))
        segments = format_segments(segments, joined=True)
        expected_text = read_file('./test/fixtures/sangre.txt').strip()

        self.assertEqual(1, len(segments))
        self.assertEqual(expected_text, segments[0].strip())

    def test_format_segments__joined_large_segment__is_shortened(self):
        segment_text = "a" * 2000
        segments = format_segments([segment_text], joined=True)

        self.assertEqual(1, len(segments))
        self.assertLess(len(segments[0]), len(segment_text))
