#! /usr/bin/env python3

import argparse
import json
import sys

from functools import reduce
from enum import Enum

from forecast import Forecast, LikelihoodType, ProblemType, ElevationType, AspectType, \
    Zone, DangerType, SizeType
from utils import is_not_None, safe, logger, Data


MAX_SEGMENTS = 10
MAX_SGEMENT_CHARS = 153

# List of valid characters to send via sms # https://en.wikipedia.org/wiki/GSM_03.38
GSM_CHARSET = ("@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?"
               "¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ`¿abcdefghijklmnopqrstuvwxyzäöñüà")

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
    ProblemType.WindSlab.name: "wind slab",
    ProblemType.LooseWet.name: "loose wet",
    ProblemType.StormSlab.name: "storm slab"
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

DANGER_TYPE_TO_TEXT = {
    DangerType.Low.name: 'low',
    DangerType.Moderate.name: 'moderate',
    DangerType.Considerable.name: 'considerable',
    DangerType.High.name: 'high',
    DangerType.Extreme.name: 'extreme',
}


class MessagePartType(Enum):
    Header = "Header"
    Danger = "Danger"
    Description = "Description"
    Problem = "Problem"
    Warning = "Warning"


class MessagePart(Data):
    def __init__(self, part_type, text):
        self.part_type = part_type
        self.text = text


LONG_MESSAGE_PART_LIST = [
    MessagePartType.Header,
    MessagePartType.Danger,
    MessagePartType.Problem,
    MessagePartType.Warning,
    MessagePartType.Description,
]


SHORT_MESSAGE_PART_LIST = [
    MessagePartType.Header,
    MessagePartType.Warning,
    MessagePartType.Danger,
    MessagePartType.Problem
]


@safe(safe_return_value="Error retrieving forecast elevation data", log=LOG)
def convert_problem_rose_elevation_to_text(elevation, problem_rose_elevation):
    aspect_entries = list(problem_rose_elevation.items())
    aspect_entries.sort(key=lambda e: ASPECT_ORDER[e[0]])
    aspect_entries = filter(lambda e: e[1] is True or e[1] is None, aspect_entries)
    aspect_entries = map(lambda e: e[0], aspect_entries)
    return "  " + ELEVATIONS_TO_TEXT.get(elevation, "") + ": " + " ".join(aspect_entries)


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
        "There is a ",
        " ".join(filter(is_not_None, [
            LIKELYHOOD_TO_TEXT.get(problem.likelyhood, None),
            SIZE_TO_TEXT.get(problem.size, None)
        ])),
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
def convert_warning_to_text(warning, long):
    title = convert_warning_title_to_text(warning)
    if long:
        return "\n".join([title, warning.description])
    else:
        return title


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
        "Avalanche dangers:",
        *map(convert_danger_to_text, dangers)
    ]))


@safe(safe_return_value="Avalanche Forecast", log=LOG)
def convert_header_to_text(forecast):
    return " - ".join(filter(is_not_None, [
        ZONE_TO_TEXT.get(forecast.zone, None),
        forecast.date]))


@safe(log=LOG)
def forecast_to_message_parts(forecast, long):
    message_parts = [
        MessagePart(MessagePartType.Header, convert_header_to_text(forecast)),
        MessagePart(MessagePartType.Danger, convert_all_dangers_to_text(forecast.dangers)),
        MessagePart(MessagePartType.Description, forecast.description),
        *[MessagePart(MessagePartType.Problem, convert_problem_to_text(p))
            for p in forecast.problems],
        *[MessagePart(MessagePartType.Warning, convert_warning_to_text(w, long))
            for w in forecast.warnings],
    ]
    message_parts = filter(lambda part: part.text is not None, message_parts)
    return list(message_parts)


def segment_reducer(new_segments, current_segment):
    join_str = "\n\n"
    if len(new_segments) == 0:
        new_segments.append(current_segment)
    elif len(current_segment) + len(new_segments[-1]) + len(join_str) < MAX_SGEMENT_CHARS:
        new_segments[-1] = join_str.join([new_segments[-1], current_segment])
    else:
        new_segments.append(current_segment)
    return new_segments


@safe(log=LOG)
def message_parts_to_segments(message_parts):
    join_str = "\n\n"
    segments = map(lambda part: part.text, message_parts)
    segments = list(reduce(segment_reducer, segments, []))

    for s in segments:
        if len(s) > MAX_SGEMENT_CHARS:
            LOG.warning("event=segment_too_large, segmentSize=%d", len(s))

    return list(segments)


@safe(log=LOG)
def filter_non_gsm_chars(text):
    return "".join(filter(lambda c: c in GSM_CHARSET, text))


@safe(log=LOG)
def forecast_to_segments(forecast, long):
    filter_list = LONG_MESSAGE_PART_LIST if long else SHORT_MESSAGE_PART_LIST

    message_parts = forecast_to_message_parts(forecast, long)
    message_parts = filter(lambda part: part.part_type in filter_list, message_parts)
    message_parts = list(message_parts)
    message_parts.sort(key=lambda part: filter_list.index(part.part_type))
    message_parts = map(lambda part:
                        MessagePart(part.part_type, filter_non_gsm_chars(part.text)),
                        message_parts)

    segments = message_parts_to_segments(message_parts)
    return segments


@safe(safe_return_value=["Error retrieving forecast"], log=LOG)
def forecast_to_text(forecast, long):
    segments = forecast_to_segments(forecast, long)

    text = "\n\n".join(segments)
    if len(text) > MAX_SEGMENTS * MAX_SGEMENT_CHARS:
        pad = "..."
        text = text[0:MAX_SEGMENTS * MAX_SGEMENT_CHARS - len(pad)] + pad
    return [text]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--long", action="store_true")
    parser.add_argument("-u", "--unsegmented", action="store_true")
    args = parser.parse_args()

    forecast = Forecast.from_json(sys.stdin)
    if args.unsegmented:
        print(forecast_to_text(forecast, args.long)[0], end='')
    else:
        json.dump(forecast_to_segments(forecast, args.long), sys.stdout, indent=4)
