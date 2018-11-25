import argparse
import logging
from moviepy.editor import *
import os
import sys
from tqdm import tqdm

from signal_process_utils import Song
import youtube_dl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--song', default=None, type=str)
parser.add_argument('-r', '--sample_rate', default=100, type=int)
parser.add_argument('-y', '--youtube', default=None, type=str)

args = parser.parse_args()
sample_rate = args.sample_rate

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
        logger.warn(f'Song {args.song} does not exist in assets folder. Exiting.')
        sys.exit()
    logger.info('Found local video file.')

s = Song(song_file)

frames = []
for offset in tqdm(range(0, s.ms, sample_rate)):
    sample_data = s.sample(offset=offset)
    piano_lit = s.generate_keyboard(sample_data)
    single_frame = ImageClip(piano_lit).set_duration(sample_rate / 1000.)
    frames.append(single_frame)

out = concatenate_videoclips(frames, method="compose")
out = out.set_audio(AudioFileClip(song_file))

# temp audio to deal with moviepy bug
out.write_videofile("test.mp4",
                    fps=1000 // sample_rate,
                    temp_audiofile="temp-audio.m4a",
                    remove_temp=True,
                    codec="libx264",
                    audio_codec="aac"
                    )
