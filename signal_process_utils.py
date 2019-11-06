#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

import pandas as pd
import psutil


def generate_frequency_table(scale=1):
    """ Run some dataframe manipluation upon import to generate the note/frequency table mappings. """

    # generate keypoints of octave 1 piano keys
    top = 12 // scale
    bottom_black = 168 // scale
    bottom_white = 229 // scale
    octave = 256 // scale

    a = [
        (22 // scale, top),
        (22 // scale, bottom_black),
        (7 // scale, bottom_black),
        (7 // scale, bottom_white),
        (43 // scale, bottom_white),
        (43 // scale, bottom_black),
        (30 // scale, bottom_black),
        (30 // scale, top),
    ]

    bb = [(30 // scale, top), (30 // scale, bottom_black), (58 // scale, bottom_black), (58 // scale, top)]

    b = [
        (58 // scale, top),
        (58 // scale, bottom_black),
        (43 // scale, bottom_black),
        (43 // scale, bottom_white),
        (79 // scale, bottom_white),
        (79 // scale, top),
    ]

    c = [
        (79 // scale, top),
        (79 // scale, bottom_white),
        (116 // scale, bottom_white),
        (116 // scale, bottom_black),
        (102 // scale, bottom_black),
        (102 // scale, top),
    ]

    db = [(102 // scale, top), (102 // scale, bottom_black), (131 // scale, bottom_black), (131 // scale, top)]

    d = [
        (131 // scale, top),
        (131 // scale, bottom_black),
        (116 // scale, bottom_black),
        (116 // scale, bottom_white),
        (153 // scale, bottom_white),
        (153 // scale, bottom_black),
        (138 // scale, bottom_black),
        (138 // scale, top),
    ]

    eb = [(138 // scale, top), (138 // scale, bottom_black), (167 // scale, bottom_black), (167 // scale, top)]

    e = [
        (167 // scale, top),
        (167 // scale, bottom_black),
        (153 // scale, bottom_black),
        (153 // scale, bottom_white),
        (190 // scale, bottom_white),
        (190 // scale, top),
    ]

    f = [
        (190 // scale, top),
        (190 // scale, bottom_white),
        (224 // scale, bottom_white),
        (224 // scale, bottom_black),
        (212 // scale, bottom_black),
        (212 // scale, top),
    ]

    gb = [(212 // scale, top), (212 // scale, bottom_black), (240 // scale, bottom_black), (240 // scale, top)]

    g = [
        (240 // scale, top),
        (240 // scale, bottom_black),
        (224 // scale, bottom_black),
        (224 // scale, bottom_white),
        (262 // scale, bottom_white),
        (262 // scale, bottom_black),
        (248 // scale, bottom_black),
        (248 // scale, top),
    ]

    ab = [
        (248 // scale, top),
        (248 // scale, bottom_black),
        (277 // scale, bottom_black),
        (277 // scale, top)
    ]

    keys = {
        'a': a,
        'bb': bb,
        'b': b,
        'c': c,
        'db': db,
        'd': d,
        'eb': eb,
        'e': e,
        'f': f,
        'gb': gb,
        'g': g,
        'ab': ab,
    }

    # dataframe to map notes, frequencies, and keyboard keys
    freqs = pd.read_csv(os.path.join('assets', 'freqs.csv'))
    df = pd.DataFrame(columns=['note', 'points'])

    c = 0
    for i in range(8):
        for note, points in keys.items():
            points = [(j + octave * i, k) for j, k in points]
            df.loc[88 - c] = [note + str(i), points]
            c += 1
    return freqs.join(df)


def get_memory_usage():
    """Returns memory usage of current process in MB. Used for logging.

    Returns:
        float: Memory usage of current process in MB.
    """
    pid = os.getpid()
    return round(psutil.Process(pid).memory_info().rss / 1e6, 2)
