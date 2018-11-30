#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
import os
import sys

import youtube_dl
from pydub import AudioSegment

from decomposer import Decomposer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--song', default=None, type=str)
parser.add_argument('-y', '--youtube', default=None, type=str)
parser.add_argument('-m', '--max_time', default=None, type=int)
parser.add_argument('-p', '--plot', default=False, type=bool)

args = parser.parse_args()

# download the song from youtube as video, cvt to mp3, cleanup
if args.youtube:
    raw_name = args.youtube.split('=')[-1]
    options = {
        # todo youtube-dl issue, cant download only audio, getting codec issue
        'outtmpl': '%(id)s',
        'format': 'bestaudio/best',
    }
    with youtube_dl.YoutubeDL(options) as ydl:
        a = ydl.download([args.youtube])
        logger.info(f'Sucessfully downloaded video file {raw_name}.')

    mp3_name = raw_name + '.mp3'
    AudioSegment.from_file(raw_name).export(mp3_name, format="mp3")
    logger.info(f'Sucessfully converted video file to mp3: {mp3_name}.')
    song_file = os.path.join('assets', mp3_name)

    try:
        os.remove(raw_name)  # clean up
        os.rename(mp3_name, song_file)
    except FileExistsError:
        pass

elif args.song:
    song_file = os.path.join('assets', args.song)
    if not os.path.isfile(song_file):
        logger.error(f'Song {args.song} does not exist in assets directory. Exiting.')
        sys.exit()
    logger.info(f'Found local video file {song_file}.')

else:
    logger.error('Must choose one option: --song or --youtube')
    sys.exit()

if not os.path.isdir('output'):
    os.mkdir('output')

decomposer = Decomposer(song_file, stop_time=args.max_time, plot=args.plot)
decomposer.cvt_mp3_to_piano()
