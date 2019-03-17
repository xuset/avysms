import unittest

from aws_lambda import sms_handler


class TestForecastToText(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_sms_handler__missing_zone__returns_help_text(self):
        event = {
            "queryStringParameters": {
                "Body": "foobar"
            }
        }
        response = sms_handler(event, None)
        self.assertIn('This is an automated text message', response["body"])
        self.assertIn('Sangre de Cristo', response["body"])

    def test_sms_handler__request_has_zone__returns_forecast(self):
        event = {
            "queryStringParameters": {
                "Body": "sangre"
            }
        }
        response = sms_handler(event, None)
        self.assertTrue(len(response["body"]) > 0)
        self.assertIn('Avalanche dangers', response["body"])
