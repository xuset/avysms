#! /usr/bin/env python3

import re
import sys
import json
import jsonpickle
from bs4 import BeautifulSoup

from forecast import Forecast, ElevationType, AspectType, ProblemType, LikelihoodType, \
    Problem, Zone, DangerType, SizeType
from utils import safe, is_not_None, logger

LOG = logger(__name__)

PROBLEM_TYPE_ID_TO_TYPE = {
    113: ProblemType.StormSlab,
    114: ProblemType.WindSlab,
    116: ProblemType.LooseWet,
    117: ProblemType.PersistentSlab,
    118: ProblemType.DeepPersistentSlab
}

PROBLEM_LIKELIHOOD_ID_TO_TYPE = {
    'Unlikely': LikelihoodType.Unlikely,
    'Possible': LikelihoodType.Possible,
    'Likely': LikelihoodType.Likely,
    'Very_Likely': LikelihoodType.VeryLikely,
    'Certain': LikelihoodType.Certain
}

ELEVATION_TYPE_TO_PROBLEM_ELEVATION_ID = {
    ElevationType.BelowTreeline: "Btl",
    ElevationType.Treeline: "Tln",
    ElevationType.AboveTreeline: "Alp"
}

DANGER_ELEVATION_ID_TO_NAME = {
    'above': ElevationType.AboveTreeline,
    'near': ElevationType.Treeline,
    'below': ElevationType.BelowTreeline,
}

DANGER_ID_TO_NAME = {
    'norating': DangerType.NoRating,
    'low': DangerType.Low,
    'moderate': DangerType.Moderate,
    'considerable': DangerType.Considerable,
    'high': DangerType.High,
    'extreme': DangerType.Extreme,
}

SIZE_ID_TO_NAME = {
    'small': SizeType.Small.name,
    'small-large': SizeType.SmallToLarge.name,
    'large': SizeType.Large.name,
    'large-vlarge': SizeType.LargeToVeryLarge.name,
    'vlarge': SizeType.VeryLarge.name,
    'vlarge-historic': SizeType.VeryLargeToHistoric.name,
    'historic': SizeType.Historic.name
}


@safe(log=LOG)
def parse_forecast_date(forecast_root):
    return forecast_root.find("h2").contents[0].strip()


@safe(log=LOG)
def parse_forecast_description(forecast_root):
    return "".join(forecast_root.find("div", attrs={"class": "fx-text-area"}).strings) \
        .replace("\u00a0", "").strip()


@safe(log=LOG)
def parse_problem_type(problem_root):
    problem_type_url = problem_root.find("a", attrs={"data-fancybox-type": "iframe"})["href"]
    problem_type_id = int(re.search(r'.*post_id=(\d+).*', problem_type_url).group(1))
    return PROBLEM_TYPE_ID_TO_TYPE[problem_type_id].name


@safe(log=LOG)
def parse_problem_likelihood(problem_root):
    likelihood_root = problem_root.find('div', attrs={'class': 'likelihood-graphic'})
    likelihood_id = likelihood_root.find('div', attrs={'class': 'on'})['id']
    return PROBLEM_LIKELIHOOD_ID_TO_TYPE[re.search(r'(\w+)_\d', likelihood_id).group(1)].name


@safe(log=LOG)
def parse_problem_size(problem_root):
    id_regex = re.compile(r"avi_size_\d+")
    size_root = problem_root.find(id=id_regex)
    return next(
        filter(
            is_not_None,
            map(
                lambda cls: SIZE_ID_TO_NAME.get(cls, None),
                size_root.get_attribute_list("class"))))


@safe(log=LOG)
def is_elevation_aspect_problematic(rose_root, elevation, aspect):
    elevation_class = ELEVATION_TYPE_TO_PROBLEM_ELEVATION_ID[elevation]
    id_regex = re.compile(aspect.value + elevation_class + r"_\d+")
    return 'on' in rose_root.find(id=id_regex).get_attribute_list("class")


@safe(log=LOG)
def parse_problem_rose(problem_root):
    rose_root = problem_root.find("div", attrs={"class": "ProblemRose"})

    problem_rose = {elevation.name:
                    {aspect.name: is_elevation_aspect_problematic(rose_root, elevation, aspect)
                     for aspect in list(AspectType)}
                    for elevation in list(ElevationType)}

    return problem_rose


@safe(log=LOG)
def parse_problem(problem_root):
    return {
        "problem_type": parse_problem_type(problem_root),
        "likelyhood": parse_problem_likelihood(problem_root),
        "size": parse_problem_size(problem_root),
        "rose": parse_problem_rose(problem_root)
    }


@safe(log=LOG)
def find_problem_root_from_table(table):
    return table.parent


@safe(safe_return_value=[], log=LOG)
def find_all_problem_roots(forecast_root):
    tables = forecast_root.find_all("table", attrs={"class": "table-persistent-slab"})
    problem_roots = map(find_problem_root_from_table, tables)
    problem_roots = filter(is_not_None, problem_roots)
    problem_roots = filter(lambda elem: 'display: none' not in str(
        elem.get('style')), problem_roots)
    return list(problem_roots)


@safe(safe_return_value=[], log=LOG)
def parse_all_problems(forecast_root):
    problems = map(parse_problem, find_all_problem_roots(forecast_root))
    problems = filter(is_not_None, problems)
    return list(problems)


@safe(log=LOG)
def parse_warning_issued_datetime(warning_root):
    meta_list = list(warning_root.find('div', attrs={'class': 'title'}).strings)
    issued_index = meta_list.index("Issued:") + 1
    return str(meta_list[issued_index]).strip()


@safe(log=LOG)
def parse_warning_expires_datetime(warning_root):
    meta_list = list(warning_root.find('div', attrs={'class': 'title'}).strings)
    expires_index = meta_list.index("Expires:") + 1
    return str(meta_list[expires_index]).strip()


@safe(log=LOG)
def parse_warning_title(warning_root):
    meta_root = warning_root.find('div', attrs={'class': 'title'})
    title_root = meta_root.find('strong')
    return str(title_root.string)


@safe(log=LOG)
def parse_warning_description(warning_root):
    content_root = warning_root.find('div', attrs={'class': 'content'})
    return "\n".join(content_root.strings).replace('\xa0', '')


@safe(log=LOG)
def parse_warning(warning_root):
    return {
        "issued": parse_warning_issued_datetime(warning_root),
        "expires": parse_warning_expires_datetime(warning_root),
        "title": parse_warning_title(warning_root),
        "description": parse_warning_description(warning_root)
    }


@safe(safe_return_value=[], log=LOG)
def parse_all_warnings(html_root):
    warning_roots = html_root.find_all('div', attrs={'class': 'avalanche-warning'})
    warnings = map(parse_warning, warning_roots)
    warnings = filter(is_not_None, warnings)
    return list(warnings)


@safe(log=LOG)
def parse_danger(danger_root):
    danger_td_class = str(danger_root.find('td', attrs={'class': 'today-text'}).attrs['class'])
    danger_elevation_id, danger_id = re.search(r'(\w+)_danger_(\w+)', danger_td_class).group(1, 2)
    return {
        "elevation": DANGER_ELEVATION_ID_TO_NAME[danger_elevation_id].name,
        "danger_type": DANGER_ID_TO_NAME[danger_id].name
    }


@safe(safe_return_value=[], log=LOG)
def parse_all_dangers(forecast_root):
    danger_roots = forecast_root.find('table', attrs={'class': 'table-treeline'}) \
                                .find('tbody').find_all('tr')
    dangers = map(parse_danger, danger_roots)
    dangers = filter(is_not_None, dangers)
    return list(dangers)


def parse_forecast(html, zone=None):
    html_root = BeautifulSoup(html, 'html.parser')
    forecast_root = html_root.find(id="avalanche-forecast")

    zone = zone.name if zone is not None else None
    date = parse_forecast_date(forecast_root)
    description = parse_forecast_description(forecast_root)
    problems = parse_all_problems(forecast_root)
    warnings = parse_all_warnings(html_root)
    dangers = parse_all_dangers(forecast_root)

    return Forecast(zone, date, description, problems, warnings, dangers)


if __name__ == "__main__":
    print(parse_forecast(sys.stdin).to_json(), end='')
