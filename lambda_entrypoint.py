import json
import sys

from text_interface import do_command

def lambda_handler(event, context):
  print('event=lambda_invoked, lambda_event={}, lambda_context={}'.format(event, context), file=sys.stderr)
  request_body = event["queryStringParameters"]["Body"]
  result = {
    "statusCode": 200,
    "headers": {
      "Content-Type": "text/plain"
    },
    "body": do_command(request_body)
  }
  print('event=lambda_return, result={}'.format(result), file=sys.stderr)
  return result

if __name__ == "__main__":
  event = {
    "queryStringParameters": {
      "Body": " ".join(sys.argv[1:])
    }
  }
  json.dump(lambda_handler(event, None), sys.stdout)
  

