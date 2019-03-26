import unittest

from aws_lambda import entrypoint
from aws_lambda_email import email_handler


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

    def test_email___not_an_inreach_email__returns_None(self):
        event = {
            "Records": [
                {
                    "ses": {
                        "mail": {
                            # This references an email that is *not* from an inreach device
                            "messageId": "h4611cb2qvoeg3gv2cn0epao07gbb4fsus3p9ag1"
                        }
                    }
                }
            ]
        }

        response_email = email_handler(event, should_reply=False)
        self.assertIsNone(response_email)

    def test_email___not_an_inreach_email__returns_None(self):
        event = {
            "Records": [
                {
                    "ses": {
                        "mail": {
                            # This references an email that is from an inreach device
                            "messageId": "u9sugnmdtpha2cvk2ok6qdtjkp3h4ali3tsenl81"
                        }
                    }
                }
            ]
        }

        inreach_response = email_handler(event, should_reply=False)
        self.assertEqual(("https://us0.inreach.garmin.com/textmessage/txtmsg"
                          "?extId=d204a435-9a39-40e0-ae79-66233c93432d"
                          "&adr=forecast%40avysms.com"), inreach_response.reply_url)
        self.assertEqual("d204a435-9a39-40e0-ae79-66233c93432d", inreach_response.guid)
        self.assertEqual("forecast@avysms.com", inreach_response.reply_address)
        self.assertIn("Avalanche dangers", "\n\n".join(inreach_response.response_segments))
