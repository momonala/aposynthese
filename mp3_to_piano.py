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


def decomposer_pipeline(arg_dict):
    """
    Run the decomposer pipeline. Includes searching for song and/or downloading Youtube video.
    Args:
        arg_dict (dict): dictionary of parsed arguments
    Returns: None
    """
    # download the song from youtube as video, cvt to mp3, cleanup
    song = arg_dict.get('song', None)
    youtube = arg_dict.get('youtube', None)
    max_time = arg_dict.get('max_time', None)
    plot = arg_dict.get('plot', False)

    if youtube:
        raw_name = youtube.split('=')[-1]
        options = {
            # todo youtube-dl issue, cant download only audio, getting codec issue
            'outtmpl': '%(id)s',
            'format': 'bestaudio/best',
        }
        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([youtube])
            logger.info(f'[PIPELINE] >>>> Sucessfully downloaded video file {raw_name}.')

        mp3_name = raw_name + '.mp3'
        AudioSegment.from_file(raw_name).export(mp3_name, format="mp3")
        logger.info(f'[PIPELINE] >>>> Sucessfully converted video file to mp3: {mp3_name}.')
        song_file = os.path.join('input', mp3_name)

        try:
            os.mkdir('input') if not os.path.isdir('input') else None
            os.mkdir('output') if not os.path.isdir('output') else None
            os.rename(mp3_name, song_file)
            os.remove(raw_name)  # clean up
        except FileExistsError:
            pass

    elif song:
        song_file = os.path.join('input', song)
        if not os.path.isfile(song_file):
            logger.error(f'[PIPELINE] >>>> Song {song} does not exist in input directory. Exiting.')
            sys.exit()
        logger.info(f'[PIPELINE] >>>> Found local video file {song_file}.')

    else:
        logger.error('[PIPELINE] >>>> Must choose one option: --song or --youtube')
        sys.exit()

    decomposer = Decomposer(song_file, stop_time=max_time, plot=plot)
    decomposer.cvt_mp3_to_piano()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--song', default=None, type=str)
    parser.add_argument('-y', '--youtube', default=None, type=str)
    parser.add_argument('-m', '--max_time', default=None, type=int)
    parser.add_argument('-p', '--plot', default=False, type=bool)

    argument_dictionary = vars(parser.parse_args())

    decomposer_pipeline(argument_dictionary)
