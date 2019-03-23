#! /usr/bin/env python3

import argparse
import json
import jsonpickle
import sys

from forecast import Forecast, LikelihoodType, ProblemType, ElevationType, AspectType, \
    Zone, DangerType, SizeType
from utils import is_not_None, safe, logger


LOG = logger(__name__)

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

SIZE_TO_TEXT = {
    SizeType.Small.name: "small",
    SizeType.SmallToLarge.name: "large",
    SizeType.Large.name: "large",
    SizeType.LargeToVeryLarge.name: "very large",
    SizeType.VeryLarge.name: "very large",
    SizeType.VeryLargeToHistoric.name: "historic",
    SizeType.Historic.name: "historic",
}

PROBLEM_TYPE_TO_TEXT = {
    ProblemType.PersistentSlab.name: "persistent slab",
    ProblemType.DeepPersistentSlab.name: "deep persistent slab",
    ProblemType.WindSlab.name: "wind slab",
    ProblemType.LooseWet.name: "loose wet",
    ProblemType.StormSlab.name: "storm slab",
    ProblemType.LooseDry.name: "loose dry",
    ProblemType.WetSlab.name: "wet slab",
}

ELEVATIONS_TO_TEXT = {
    ElevationType.BelowTreeline.name: "Below TL",
    ElevationType.Treeline.name: "Near  TL",
    ElevationType.AboveTreeline.name: "Above TL",
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

DANGER_TYPE_TO_TEXT = {
    DangerType.NoRating.name: 'No rating',
    DangerType.Low.name: 'Low',
    DangerType.Moderate.name: 'Moderate',
    DangerType.Considerable.name: 'Considerable',
    DangerType.High.name: 'High',
    DangerType.Extreme.name: 'Extreme',
}


@safe(safe_return_value="Unknown", log=LOG)
def convert_problem_rose_elevation_aspect_to_text(problem_rose_elevation):
    aspect_entries = list(problem_rose_elevation.items())
    aspect_entries.sort(key=lambda e: ASPECT_ORDER[e[0]])
    aspect_entries = filter(lambda e: e[1] is True or e[1] is None, aspect_entries)
    aspect_entries = list(map(lambda e: e[0], aspect_entries))

    if len(aspect_entries) == 0:
        return "Unlikely"
    else:
        return " ".join(aspect_entries)


@safe(safe_return_value="Error", log=LOG)
def convert_problem_rose_elevation_name_to_text(elevation):
    return ELEVATIONS_TO_TEXT[elevation]


@safe(safe_return_value="Error retrieving forecast elevation data", log=LOG)
def convert_problem_rose_elevation_to_text(elevation, problem_rose_elevation):
    aspect_text = convert_problem_rose_elevation_aspect_to_text(problem_rose_elevation)
    elevation_name = convert_problem_rose_elevation_name_to_text(elevation)
    return "  " + elevation_name + ": " + aspect_text


@safe(safe_return_value="", log=LOG)
def convert_problem_rose_to_text(problem_rose):
    elevation_entries = list(problem_rose.items())
    elevation_entries.sort(key=lambda e: ELEVATION_ORDER[e[0]])
    elevation_entries = map(lambda e: convert_problem_rose_elevation_to_text(*e), elevation_entries)
    elevation_entries = filter(is_not_None, elevation_entries)
    return "\n".join(elevation_entries)


@safe(safe_return_value="Error retrieving forecast problems", log=LOG)
def convert_problem_to_text(problem):
    return "".join([
        " ".join(filter(is_not_None, [
            LIKELYHOOD_TO_TEXT.get(problem.likelyhood, None),
            SIZE_TO_TEXT.get(problem.size, None)
        ])).capitalize(),
        " ",
        PROBLEM_TYPE_TO_TEXT.get(problem.problem_type, "unknown"),
        " avalanche problem",
        "\n",
        convert_problem_rose_to_text(problem.rose)
    ])


@safe(safe_return_value="Avalanche warning:", log=LOG)
def convert_warning_title_to_text(warning):
    return (
        " ".join(filter(is_not_None, [
            warning.title if warning.title is not None else "Avalanche warning",
            "expires on " + warning.expires if warning.expires is not None else None]))
        + ":")


@safe(log=LOG)
def convert_warning_to_text(warning):
    return convert_warning_title_to_text(warning)


@safe(log=LOG)
def convert_danger_to_text(danger):
    return "".join([
        "  ",
        ELEVATIONS_TO_TEXT[danger.elevation],
        ": ",
        DANGER_TYPE_TO_TEXT[danger.danger_type]
    ])


@safe(log=LOG)
def convert_all_dangers_to_text(dangers):
    dangers.sort(key=lambda d: ELEVATION_ORDER[d.elevation])
    return "\n".join(filter(is_not_None, [
        "Avalanche dangers",
        *map(convert_danger_to_text, dangers)
    ]))


@safe(safe_return_value="Avalanche Forecast", log=LOG)
def convert_header_to_text(forecast):
    return " - ".join(filter(is_not_None, [
        ZONE_TO_TEXT.get(forecast.zone, None),
        forecast.date]))


@safe(log=LOG)
def forecast_to_segments(forecast):
    segments = [
        convert_header_to_text(forecast),
        convert_all_dangers_to_text(forecast.dangers),
        *[convert_problem_to_text(p) for p in forecast.problems],
        *[convert_warning_to_text(w) for w in forecast.warnings],
    ]

    segments = filter(lambda s: s is not None, segments)
    return list(segments)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    forecast = Forecast.from_json(sys.stdin)
    print(jsonpickle.encode(forecast_to_segments(forecast)), end='')
