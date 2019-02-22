import traceback

def safe_eval(eval, *args, safe_return_value=None, **kwargs):
  try:
    return eval(*args, **kwargs)
  except Exception:
    traceback.print_exc(file=sys.stderr)
  return safe_return_value
