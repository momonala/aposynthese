#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd


def generate_frequency_table():
    """ Run some dataframe manipluation upon import to generate the note/frequency table mappings. """

    # dataframe to map notes, frequencies, and keyboard keys
    freqs = pd.read_csv(os.path.join('assets', 'freqs.csv'))
    freqs = freqs.iloc[1:, :4]
    freqs['Helmholtzname'] = freqs.Helmholtzname.apply(lambda x: x.replace('′', ''))
    freqs['Helmholtzname'] = freqs.Helmholtzname.apply(lambda x: x.replace('͵', ''))
    freqs['Helmholtzname'] = freqs.Helmholtzname.apply(lambda x: x.split(' ')[0])
    freqs['Helmholtzname'] = freqs.Helmholtzname.apply(lambda x: x.upper())
    freqs['Frequency (Hz)'] = freqs['Frequency (Hz)'].astype(np.float16)
    freqs['Keynumber'] = freqs['Keynumber'].astype(np.uint8)
    freqs = freqs[freqs.Keynumber <= 88]
    freqs = freqs.sort_values('Keynumber', ascending=False)
    freqs.index = range(1, 89)

    # generate keypoints of octave 1 piano keys localized via `utils/localize_keyboard_mappings.py`

    ab = np.array([[8, 246], [162, 247], [162, 275], [8, 276]])
    a = np.array([[8, 276], [162, 275], [162, 262], [224, 262], [224, 298], [162, 297], [162, 283]])
    bb = np.array([[8, 28], [162, 29], [162, 57], [8, 58]])
    b = np.array([[8, 58], [162, 57], [162, 43], [224, 42], [224, 78], [8, 78]])
    c = np.array([[8, 78], [224, 78], [224, 115], [162, 115], [162, 102], [8, 101]])
    db = np.array([[8, 101], [162, 102], [162, 130], [8, 131]])
    d = np.array([[8, 131], [162, 130], [162, 115], [224, 115], [224, 152], [162, 152], [162, 137]])
    eb = np.array([[8, 131], [162, 137], [162, 165], [8, 166]])
    e = np.array([[8, 166], [162, 165], [162, 152], [224, 152], [224, 188], [8, 188]])
    f = np.array([[8, 188], [224, 188], [224, 224], [162, 223], [162, 210], [8, 209]])
    gb = np.array([[8, 209], [162, 210], [162, 238], [8, 239]])
    g = np.array([[8, 239], [162, 238], [162, 223], [224, 224], [224, 262], [162, 262], [162, 247], [8, 246]])

    keys = {
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
        'a': a,
    }

    j = 1
    octave = 255
    df = pd.DataFrame(columns=['note', 'points'])
    for i in range(0, 8):
        for root, orig_key in keys.items():
            key = orig_key.copy()
            if root not in ['bb', 'b'] and i == 7:
                continue
            if i != 0:
                key[:, 1] = key[:, 1] + octave * i
            df.loc[88 - j] = [root + str(i), list(key)]
            j += 1
    return freqs.join(df)
