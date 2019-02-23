
class Forecast(object):
  def __init__(self, date, description):
    self.date = date
    self.description = description

  def __str__(self):
    return str(dict(self))

  def __iter__(self):
    return iter(self.__dict__.items())
