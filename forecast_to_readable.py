import sys
import json

from forecast import Forecast, LikelihoodType, ProblemType, ElevationType, AspectType, Zone
from utils import is_not_None, safe

ZONE_TO_TEXT = {
  Zone.Steamboat.name: "Steamboat & Flat Tops",
  Zone.FrontRange.name: "Front Range",
  Zone.Vail.name: "Vail & Summit County",
  Zone.Sawatch.name: "Sawatch",
  Zone.Aspen.name: "Aspen",
  Zone.Gunnison.name: "Gunnison",
  Zone.GrandMesa.name: "Grand Mesa",
  Zone.NorthSanJuan.name: "North San Juan",
  Zone.SouthSanJuan.name: "South San Juan",
  Zone.SangreDeCristo.name: "Sangre De Cristo",
}

LIKELYHOOD_TO_TEXT = {
  LikelihoodType.Unlikely.name: "unlikely",
  LikelihoodType.Possible.name: "possible",
  LikelihoodType.Likely.name: "likely",
  LikelihoodType.VeryLikely.name: "very likely",
}

PROBLEM_TYPE_TO_TEXT = {
  ProblemType.PersistentSlab.name: "persistent slab",
  ProblemType.WindSlab.name: "wind slab",
  ProblemType.LooseWet.name: "loose wet"
}

ELEVATIONS_TO_TEXT = {
  ElevationType.BelowTreeline.name: "Below treeline",
  ElevationType.Treeline.name: "Treeline",
  ElevationType.AboveTreeline.name: "Above treeline",
}

ELEVATION_ORDER = {
  ElevationType.BelowTreeline.name: 0,
  ElevationType.Treeline.name: 1,
  ElevationType.AboveTreeline.name: 2
}

ASPECT_ORDER = {
  AspectType.N.name: 0,
  AspectType.NE.name: 1,
  AspectType.E.name: 2,
  AspectType.SE.name: 3,
  AspectType.S.name: 4,
  AspectType.SW.name: 5,
  AspectType.W.name: 6,
  AspectType.NW.name: 7
}

@safe(safe_return_value="Error retrieving forecast elevation data")
def convert_problem_rose_elevation_to_human_readable(elevation, problem_rose_elevation):
  aspect_entries = list(problem_rose_elevation.items())
  aspect_entries.sort(key=lambda e: ASPECT_ORDER[e[0]])
  aspect_entries = filter(lambda e: e[1] == True or e[1] == None, aspect_entries)
  aspect_entries = map(lambda e: e[0], aspect_entries)
  return "    " + ELEVATIONS_TO_TEXT.get(elevation, "") + ": " + " ".join(aspect_entries)

@safe(safe_return_value="")
def convert_problem_rose_to_human_readable(problem_rose):
  elevation_entries = list(problem_rose.items())
  elevation_entries.sort(key=lambda e: ELEVATION_ORDER[e[0]])
  elevation_entries = map(lambda e: convert_problem_rose_elevation_to_human_readable(*e), elevation_entries)
  elevation_entries = filter(is_not_None, elevation_entries)
  return "\n".join(elevation_entries)

@safe(safe_return_value="Error retrieving forecast problems")
def convert_problem_to_human_readable(problem):
  return "".join([
    "There is a ",
    LIKELYHOOD_TO_TEXT.get(problem.likelyhood, ""),
    " ",
    PROBLEM_TYPE_TO_TEXT.get(problem.problem_type, "unknown"),
    " avalanche problem",
    "\n",
    convert_problem_rose_to_human_readable(problem.rose)
  ])

@safe(safe_return_value="Avalanche warning:")
def convert_warning_title_to_human_readable(warning):
  return (
    " ".join(filter(is_not_None, [
      warning.title if warning.title is not None else "Avalanche warning",
      "expires on " + warning.expires if warning.expires is not None else None]))
    + ":")

@safe()
def convert_warning_to_human_readable(warning):
  return "\n".join([
    convert_warning_title_to_human_readable(warning),
    warning.description])

@safe("Unable to retrieve avalanche watches")
def convert_all_warnings_to_human_readable(warnings):
  return "\n\n".join(map(convert_warning_to_human_readable, warnings))

@safe(safe_return_value="Error retrieving forecast")
def convert_forecast_to_human_readable_text(forecast):
  return '\n\n'.join(filter(is_not_None, [
    " - ".join(filter(is_not_None, [ZONE_TO_TEXT.get(forecast.zone, None), forecast.date])),
    forecast.description,
    *map(convert_problem_to_human_readable, forecast.problems),
    convert_all_warnings_to_human_readable(forecast.warnings)
  ]))

if __name__ == "__main__":
  forecast = Forecast.from_json(sys.stdin)
  print(convert_forecast_to_human_readable_text(forecast))
  
  
