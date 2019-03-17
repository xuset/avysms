import json
import unittest

from bs4 import BeautifulSoup

from test.utils import read_file
from caic_html_to_forecast import parse_forecast, parse_problem_type, PROBLEM_TYPE_ID_TO_TYPE
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

    def test_parse_problem_type__html_has_all_problem_types__all_parsed(self):
        problem_type_html_template = \
            '<div>' + \
            '    <a ' + \
            '        data-fancybox-type="iframe" ' + \
            '        href="https://avalanche.state.co.us/caic/info.php?post_id={}">' + \
            '    </a>' + \
            '</div>'

        for problem_type_id, problem_type in PROBLEM_TYPE_ID_TO_TYPE.items():
            problem_type_html = problem_type_html_template.replace('{}', str(problem_type_id))
            problem_root = BeautifulSoup(problem_type_html, 'html.parser')

            problem_type_name = parse_problem_type(problem_root)

            self.assertEqual(problem_type.name, problem_type_name)
