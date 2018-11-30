#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
import os
import sys

from decomposer import Decomposer
import youtube_dl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--song', default=None, type=str)
parser.add_argument('-y', '--youtube', default=None, type=str)
parser.add_argument('-p', '--plot', default=False, type=bool)

args = parser.parse_args()

if args.youtube:
    raw_name = args.youtube.split('=')[-1]
    options = {
        'format': 'bestaudio/best',
        'extractaudio': True,  # only keep the audio
        'audioformat': "mp3",  # convert to mp3
        'outtmpl': '%(id)s',   # name the file the ID of the video
        'noplaylist': True,    # only download single song, not playlist
    }

    with youtube_dl.YoutubeDL(options) as ydl:
        a = ydl.download([args.youtube])
        mp3_name = raw_name + '.mp3'
        os.rename(raw_name, mp3_name)
        logger.info(f'Sucessfully downloaded video file {mp3_name}.')

    song_file = os.path.join('assets', mp3_name)
    try:
        os.rename(mp3_name, song_file)
    except FileExistsError:
        pass
else:
    song_file = os.path.join('assets', args.song)
    if not os.path.isfile(song_file):
        logger.warning(f'Song {args.song} does not exist in assets folder. Exiting.')
        sys.exit()
    logger.info('Found local video file.')

decomposer = Decomposer(song_file, plot=args.plot)
decomposer.cvt_mp3_to_piano()
