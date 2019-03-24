import unittest

from aws_lambda import entrypoint
from aws_lambda_email import email_handler, get_email_body


class TestForecastToText(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_sms___missing_zone__returns_help_text(self):
        event = {
            "queryStringParameters": {
                "Body": "foobar"
            }
        }
        response = entrypoint(event, context=None)
        self.assertIn('This is an automated service', response["body"])
        self.assertIn('Sangre de Cristo', response["body"])

    def test_sms___request_has_zone__returns_forecast(self):
        event = {
            "queryStringParameters": {
                "Body": "sangre"
            }
        }
        response = entrypoint(event, context=None)
        self.assertTrue(len(response["body"]) > 0)
        self.assertIn('Avalanche dangers', response["body"])

    def test_email___request_has_zone__returns_forecast(self):
        event = {
            "Records": [
                {
                    "ses": {
                        "mail": {
                            # This references an email requesting the 'front range' forecast
                            "messageId": "h4611cb2qvoeg3gv2cn0epao07gbb4fsus3p9ag1"
                        }
                    }
                }
            ]
        }

        response_email = email_handler(event, should_reply=False)
        response_email_body = get_email_body(response_email)
        self.assertTrue(len(response_email_body) > 0)
        self.assertIn('Avalanche dangers', response_email_body)
