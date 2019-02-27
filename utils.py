import sys
import traceback

def is_not_None(obj):
  return obj is not None

def safe(function, safe_return_value=None):
  def internal(*args, **kwargs):
    return safe_eval(function, *args, safe_return_value=safe_return_value, **kwargs)
  return internal

def safe_eval(eval, *args, safe_return_value=None, **kwargs):
  try:
    return eval(*args, **kwargs)
  except Exception:
    traceback.print_exc(file=sys.stderr)
  return safe_return_value
