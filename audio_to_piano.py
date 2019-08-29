#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import logging
import os
import sys
import traceback
from glob import glob

import youtube_dl

from decomposer import Decomposer

# logger with special stream handling to output to stdout in Node.js
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
stdout_handler.setLevel(logging.INFO)
logger.addHandler(stdout_handler)

existing_inputs = [x.strip('.wav').strip('input/') for x in glob('input/*wav')]
existing_ouputs = [x.strip('.mp4').strip('output/') for x in glob('output/*mp4')]


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
        'outtmpl': '%(id)s' + '.mp4',
        'format': 'bestaudio/best',
    }
    with youtube_dl.YoutubeDL(options) as ydl:
        try:
            ydl.download([youtube_url])
            logger.info(f'[PIPELINE] >>>> Sucessfully downloaded video file {youtube_id}.')
            try:
                # use ffmpeg to conver the .mp4 file to a (compressed) .wav
                wav_name = youtube_id + '.wav'
                os.system(f'ffmpeg -y -i {youtube_id}.mp4 -f mp3 -ab 192000 -vn input/{youtube_id}.mp3')
                os.system(f'ffmpeg -y -i input/{youtube_id}.mp3 -acodec pcm_u8 -ar 22050 input/{youtube_id}.wav')
                logger.info(f'[PIPELINE] >>>> Sucessfully converted video file to wav: {wav_name}.')
            except FileNotFoundError:
                msg = (
                    f'[PIPELINE] >>>> Youtube download and/or wav conversion failed for [{wav_name}]. '
                    f'Double check that URL is valid.'
                )
                logger.error(msg)
                raise DecomposerError(msg)

            # clean up
            os.remove(youtube_id + '.mp4')
            os.remove(os.path.join('input', youtube_id + '.mp3'))
            song_file = os.path.join('input', wav_name)
            return song_file

        except youtube_dl.utils.DownloadError:
            msg = f'{youtube_url} is not a valid YouTube URL.'
            logger.error(f'[PIPELINE] >>>> {msg}')
            raise DecomposerError(msg)


def _handle_youtube_option(youtube_url):
    """ Logic to handle option if input media is a YouTube video."""
    if 'https://www.youtube.com/watch?v=' not in youtube_url:
        msg = f'{youtube_url} is not a valid YouTube URL'
        logger.error(f'[PIPELINE] >>>> {msg}')
        raise DecomposerError(msg)
    youtube_id = youtube_url.split('=')[-1]

    # Download the song if needed
    if youtube_id not in existing_inputs:
        logger.info(f'[PIPELINE] >>>> Song not found in input database. Downloading {youtube_id}')
        _download_youtube_vid(youtube_url, youtube_id)

    # Decompose if not done already
    if youtube_id not in existing_ouputs:
        logger.info(f'[PIPELINE] >>>> Song not found in output database. Decomposing {youtube_id}')
        return os.path.join('input', youtube_id + '.wav')
    else:
        logger.info(f'[PIPELINE] >>>> {youtube_id} exists in output database. Use cached.')
        return None


def _handle_local_song_option(song):
    """ Logic to handle option if input media is a predownloaded wav. """
    song = song.strip('.wav')
    if song not in existing_inputs:
        logger.error(f'[PIPELINE] >>>> Song {song} does not exist in input directory. Exiting.')
        return None
    logger.info(f'[PIPELINE] >>>> Found local video file {song}.')

    # Decompose if not done already
    if song not in existing_ouputs:
        logger.info(f'[PIPELINE] >>>> Song not found in output database. Decomposing {song}')
        return os.path.join('input', song + '.wav')
    else:
        logger.info(f'[PIPELINE] >>>> {song} exists in output database. Use cached.')
        return None


def decomposer_pipeline(arg_dict):
    """
    Run the decomposer pipeline. Includes searching for song and/or downloading Youtube video.
    Args:
        arg_dict (dict): dictionary of parsed arguments
    Returns: None
    """
    # download the song from youtube as video, cvt to wav, cleanup
    song = arg_dict.get('song', None)
    youtube_url = arg_dict.get('youtube', None)
    max_time = arg_dict.get('max_time', None)

    setup_dirs()

    # handle downloading and setup based on media input type
    if youtube_url:
        input_song = _handle_youtube_option(youtube_url)
    elif song:
        input_song = _handle_local_song_option(song)
    else:
        msg = '[PIPELINE] >>>> Must choose one option: --song or --youtube'
        logger.error(msg)
        raise DecomposerError(msg)

    # Decompose the song if needed
    if input_song:
        try:
            Decomposer(input_song, stop_time=max_time, scale=2).cvt_audio_to_piano()
            logger.info(f'[PIPELINE] >>>> Song sucessfully decomposed!')
        except Exception:
            logger.error(traceback.print_exc())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--song', default=None, type=str)
    parser.add_argument('-y', '--youtube', default=None, type=str)
    parser.add_argument('-m', '--max_time', default=None, type=int)
    parser.add_argument('-p', '--plot', default=False, type=bool)

    argument_dictionary = vars(parser.parse_args())

    decomposer_pipeline(argument_dictionary)
