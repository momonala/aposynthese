#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
import os
from glob import glob

import youtube_dl
from pydub import AudioSegment

from decomposer import Decomposer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

existing_files = [x.strip('.mp4').strip('output/') for x in glob('output/*mp4')]


class DecomposerError(Exception):
    def __init__(self, message=''):
        self.message = message


def setup_dirs():
    """Setup up the input and output dirs if starting from scratch"""
    try:
        os.mkdir('input') if not os.path.isdir('input') else None
        os.mkdir('output') if not os.path.isdir('output') else None
    except FileExistsError:
        pass


def _download_youtube_vid(youtube_url, youtube_id):
    """
    Download Youtube video.
    Args:
        youtube_url (str): youtube video url
    Returns:
        raw_name (str): the youtube id hash only
    """
    options = {
        # todo youtube-dl issue, cant download only audio, getting codec issue
        'outtmpl': '%(id)s',
        'format': 'bestaudio/best',
    }
    with youtube_dl.YoutubeDL(options) as ydl:
        try:
            ydl.download([youtube_url])
            logger.info(f'[PIPELINE] >>>> Sucessfully downloaded video file {youtube_id}.')

            mp3_name = youtube_id + '.mp3'
            AudioSegment.from_file(youtube_id).export(mp3_name, format="mp3")
            logger.info(f'[PIPELINE] >>>> Sucessfully converted video file to mp3: {mp3_name}.')

            song_file = os.path.join('input', mp3_name)
            os.rename(mp3_name, song_file)
            os.remove(youtube_id)  # clean up
            return song_file

        except youtube_dl.utils.DownloadError:
            msg = f'{youtube_id} is not a valid YouTube ID.'
            logger.error(f'[PIPELINE] >>>> {msg}')
            raise DecomposerError(msg)


def decomposer_pipeline(arg_dict):
    """
    Run the decomposer pipeline. Includes searching for song and/or downloading Youtube video.
    Args:
        arg_dict (dict): dictionary of parsed arguments
    Returns: None
    """
    # download the song from youtube as video, cvt to mp3, cleanup
    song = arg_dict.get('song', None)
    youtube_url = arg_dict.get('youtube', None)
    max_time = arg_dict.get('max_time', None)
    plot = arg_dict.get('plot', False)

    setup_dirs()

    if youtube_url:
        if 'https://www.youtube.com/watch?v=' not in youtube_url:
            msg = f'{youtube_url} is not a valid YouTube ID'
            logger.error(f'PIPELINE >>>> {msg}')
            return None

        youtube_id = youtube_url.split('=')[-1]
        if youtube_id not in existing_files:
            logger.info(f'PIPELINE >>>> Song not found in database. Decomposing {youtube_id}')
            try:
                song_file = _download_youtube_vid(youtube_url, youtube_id)
            except DecomposerError:
                return None
        else:
            logger.info(f'PIPELINE >>>> {youtube_id} exists in database.')
            song_file = os.path.join('input', youtube_id+'.mp3')

    elif song:
        song_file = os.path.join('input', song)
        if not os.path.isfile(song_file):
            logger.error(f'[PIPELINE] >>>> Song {song} does not exist in input directory. Exiting.')
            return None
        logger.info(f'[PIPELINE] >>>> Found local video file {song_file}.')

    else:
        logger.error('[PIPELINE] >>>> Must choose one option: --song or --youtube')
        return None

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
