import re
import sys
import json
import jsonpickle
from bs4 import BeautifulSoup

from forecast import Forecast, ElevationType, AspectType, ProblemType, LikelihoodType, Problem, Zone
from utils import safe_eval, safe, is_not_None

PROBLEM_TYPE_ID_TO_NAME = {
  117: ProblemType.PersistentSlab,
  116: ProblemType.LooseWet,
  114: ProblemType.WindSlab
}

PROBLEM_LIKELIHOOD_ID_TO_NAME = {
  'Unlikely': LikelihoodType.Unlikely,
  'Possible': LikelihoodType.Possible,
  'Likely': LikelihoodType.Likely,
  'Very_Likely': LikelihoodType.VeryLikely,
  'Certain': LikelihoodType.Certain
}

@safe()
def parse_forecast_date(root):
  return root.find_all("h2")[0].contents[0].strip()

@safe()
def parse_forecast_description(root):
  return root.find_all("div", attrs={"class": "fx-text-area"})[0] \
    .find("p").string.replace("\u00a0", "")

@safe()
def parse_problem_type(problem_root):
  problem_type_url = problem_root.find("a", attrs={"data-fancybox-type": "iframe"})["href"]
  problem_type_id = int(re.search('.*post_id=(\d+).*', problem_type_url).group(1))
  return PROBLEM_TYPE_ID_TO_NAME[problem_type_id].name

@safe()
def parse_problem_likelihood(problem_root):
  likelihood_root = problem_root.find_all('div', attrs={'class': 'likelihood-graphic'})[0]
  likelihood_id = likelihood_root.find_all('div', attrs={'class': 'on'})[0]['id']
  return PROBLEM_LIKELIHOOD_ID_TO_NAME[re.search('(\w+)_\d', likelihood_id).group(1)].name

@safe()
def parse_problem_size(problem_root):
  return None

@safe()
def is_elevation_aspect_problematic(rose_root, elevation, aspect):
  return 'on' in rose_root.find(id=re.compile(aspect.value + elevation.value + "_\d")).get_attribute_list("class")

@safe()
def parse_forecast_problem_rose(problem_root):
  rose_root = problem_root.find_all("div", attrs={"class": "ProblemRose"})[0]

  problem_rose = {elevation.name:
    {aspect.name: is_elevation_aspect_problematic(rose_root, elevation, aspect)
      for aspect in list(AspectType)}
        for elevation in list(ElevationType)}

  return problem_rose

@safe()
def parse_forecast_problem(problem_root):
  problem_type = parse_problem_type(problem_root)
  problem_likelihood = parse_problem_likelihood(problem_root)
  problem_size = parse_problem_size(problem_root)
  problem_rose = parse_forecast_problem_rose(problem_root)

  return {
    "problem_type": problem_type,
    "likelyhood": problem_likelihood,
    "size": problem_size,
    "rose": problem_rose
  }

@safe()
def find_forecast_problem_root_from_table(table):
  return table.parent

@safe()
def find_forecast_problem_roots(root):
  tables = root.find_all("table", attrs={"class": "table-persistent-slab"})
  problem_roots = map(find_forecast_problem_root_from_table, tables)
  problem_roots = filter(is_not_None, problem_roots)
  problem_roots = filter(lambda elem: elem.get('style') != 'display: none;', problem_roots)
  return list(problem_roots)

@safe()
def parse_all_forecast_problems(root):
  return list(map(parse_forecast_problem, find_forecast_problem_roots(root)))

def parse_forecast(html, zone=None):
  soup = BeautifulSoup(html, 'html.parser')
  root = soup.find(id="avalanche-forecast")

  zone = zone.name if zone is not None else None

  date = parse_forecast_date(root)

  description = parse_forecast_description(root)

  problems = parse_all_forecast_problems(root)

  return Forecast(zone, date, description, problems)

if __name__ == "__main__":
  print(parse_forecast(sys.stdin).to_json())
