#! /usr/bin/env python3

import argparse
import sys
from functools import reduce

import jsonpickle

from utils import safe, logger

MAX_SEGMENTS = 10

MAX_SGEMENT_CHARS = 153

# List of valid characters to send via sms # https://en.wikipedia.org/wiki/GSM_03.38
GSM_CHARSET = ("@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?"
               "¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ`¿abcdefghijklmnopqrstuvwxyzäöñüà")

LOG = logger(__name__)


@safe(log=LOG)
def filter_non_gsm_chars(text):
    return "".join(filter(lambda c: c in GSM_CHARSET, text))


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
def reduce_segments(segments):
    join_str = "\n\n"
    segments = map(filter_non_gsm_chars, segments)
    segments = reduce(segment_reducer, segments, [])
    segments = list(segments)

    return segments


def join_segments(segments):
    text = "\n\n".join(segments)
    max_chars = MAX_SEGMENTS * MAX_SGEMENT_CHARS
    if len(text) > max_chars:
        pad = "..."
        text = text[0:max_chars - len(pad)] + pad
    return [text]


def log_warning_for_large_segment(segments, segment_warn_length):
    for s in segments:
        if len(s) > segment_warn_length:
            LOG.warning("event=segment_too_large, segmentSize=%d", len(s))


def format_segments(segments, joined):
    segment_warn_length = MAX_SGEMENT_CHARS
    segments = reduce_segments(segments)

    if joined:
        segment_warn_length = MAX_SEGMENTS * MAX_SGEMENT_CHARS
        segments = join_segments(segments)

    log_warning_for_large_segment(segments, segment_warn_length)

    return segments


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--raw", action="store_true")
    parser.add_argument("-j", "--joined", action="store_true")
    args = parser.parse_args()

    segments = jsonpickle.decode(sys.stdin.read())
    segments = format_segments(segments, args.joined)
    segments = segments if args.raw else "\n\n".join(segments)

    print(segments, end='')
