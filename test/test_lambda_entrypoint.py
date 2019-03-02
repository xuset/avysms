import unittest

from lambda_entrypoint import lambda_handler

class TestForecastToText(unittest.TestCase):

  def setUp(self):
    self.maxDiff = None
  
  def test_lambda_handler__missing_zone__returns_help_text(self):
    event = {
      "queryStringParameters": {
        "Body": "foobar"
      }
    }
    response = lambda_handler(event, None)
    self.assertIn('This is an automated avalanche', response["body"])
    self.assertIn('Sangre de Cristo', response["body"])

  def test_lambda_handler__request_has_zone__returns_forecast(self):
    event = {
      "queryStringParameters": {
        "Body": "sangre"
      }
    }
    response = lambda_handler(event, None)
    self.assertTrue(len(response["body"]) > 0)
    self.assertIn('Avalanche dangers', response["body"])
