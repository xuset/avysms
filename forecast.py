from enum import Enum

class AspectType(Enum):
  N = "N"
  NE = "NE"
  E = "E"
  SE = "SE"
  S = "S"
  SW = "SW"
  W = "W"
  NW = "NW"

class ElevationType(Enum):
  BelowTreeline = "Btl"
  Treeline = "Tln"
  AboveTreeline = "Alp"

class LikelihoodType(Enum):
  Unlikely = 0
  Possible = 1
  Likely = 2
  VeryLikely = 3
  Certain = 4

class SizeType(Enum):
  Small = 0
  Large = 1
  VeryLarge = 2
  Historic = 3

class ProblemType(Enum):
  PersistentSlab = "PersistentSlab"
  WindSlab = "WindSlab"
  LooseWet = "LooseWet"

class Forecast(object):
  def __init__(self, date, description):
    self.date = date
    self.description = description

  def __str__(self):
    return str(dict(self))

  def __iter__(self):
    return iter(self.__dict__.items())
