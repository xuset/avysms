import jsonpickle
import json
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

class DangerType(Enum):
  Low = 0
  Moderate = 1
  Considerable = 2
  High = 3
  Extreme = 4

class ProblemType(Enum):
  PersistentSlab = "PersistentSlab"
  WindSlab = "WindSlab"
  LooseWet = "LooseWet"

class Zone(Enum):
  Steamboat = "Steamboat"
  FrontRange = "FrontRange"
  Vail = "Vail"
  Sawatch = "Sawatch"
  Aspen = "Aspen"
  Gunnison = "Gunnison"
  GrandMesa = "GrandMesa"
  NorthSanJuan = "NorthSanJuan"
  SouthSanJuan = "SouthSanJuan"
  SangreDeCristo = "SangreDeCristo"

class Data(object):
  def __str__(self):
    return str(dict(self))

  def __iter__(self):
    return iter(json.loads(jsonpickle.encode(self, unpicklable=False)).items())

  def to_json(self):
    return jsonpickle.encode(self)

  @staticmethod
  def from_json(json_str):
    return jsonpickle.decode(json_str.read())

class Danger(Data):
  def __init__(self, elevation, danger_type):
    self.elevation = elevation
    self.danger_type = danger_type

class Problem(Data):
  def __init__(self, rose, problem_type, size, likelyhood):
    self.rose = rose
    self.problem_type = problem_type
    self.size = size
    self.likelyhood = likelyhood

class Warning(Data):
  def __init__(self, issued, expires, title, description):
    self.issued = issued
    self.expires = expires
    self.title = title
    self.description = description

class Forecast(Data):
  def __init__(self, zone, date, description, problems, warnings, dangers):
    self.zone = zone
    self.date = date
    self.description = description
    self.dangers = list(map(lambda d: Danger(**d), dangers))
    self.problems = list(map(lambda p: Problem(**p), problems))
    self.warnings = list(map(lambda w: Warning(**w), warnings))
