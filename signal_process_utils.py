#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pandas as pd


def generate_frequency_table():
    """ Run some dataframe manipluation upon import to generate the note/frequency table mappings. """

    # generate keypoints of octave 1 piano keys
    top = 12
    bottom_black = 168
    bottom_white = 229
    octave = 256

    a = [(22, top),
         (22, bottom_black),
         (7, bottom_black),
         (7, bottom_white),
         (43, bottom_white),
         (43, bottom_black),
         (30, bottom_black),
         (30, top)]

    bb = [(30, top),
          (30, bottom_black),
          (58, bottom_black),
          (58, top)]

    b = [(58, top),
         (58, bottom_black),
         (43, bottom_black),
         (43, bottom_white),
         (79, bottom_white),
         (79, top)]

    c = [(79, top),
         (79, bottom_white),
         (116, bottom_white),
         (116, bottom_black),
         (102, bottom_black),
         (102, top)]

    db = [(102, top),
          (102, bottom_black),
          (131, bottom_black),
          (131, top)]

    d = [(131, top),
         (131, bottom_black),
         (116, bottom_black),
         (116, bottom_white),
         (153, bottom_white),
         (153, bottom_black),
         (138, bottom_black),
         (138, top)]

    eb = [(138, top),
          (138, bottom_black),
          (167, bottom_black),
          (167, top)]

    e = [(167, top),
         (167, bottom_black),
         (153, bottom_black),
         (153, bottom_white),
         (190, bottom_white),
         (190, top)]

    f = [(190, top),
         (190, bottom_white),
         (224, bottom_white),
         (224, bottom_black),
         (212, bottom_black),
         (212, top)]

    gb = [(212, top),
          (212, bottom_black),
          (240, bottom_black),
          (240, top)]

    g = [(240, top),
         (240, bottom_black),
         (224, bottom_black),
         (224, bottom_white),
         (262, bottom_white),
         (262, bottom_black),
         (248, bottom_black),
         (248, top)]

    ab = [(248, top),
          (248, bottom_black),
          (277, bottom_black),
          (277, top)]

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
