
class Forecast(object):
  def __init__(self, description):
    self.description = description

  def __str__(self):
    return str(self.__dict__)

  @staticmethod
  def from_dict(from_dict):
    return Forecast(**from_dict)

  def to_dict(self):
    return self.__dict__
