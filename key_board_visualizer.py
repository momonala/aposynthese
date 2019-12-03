#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os

import numpy as np
from PIL import Image, ImageDraw

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KeyBoardVisualizer(object):
    def __init__(self, decomposer, scale=2):
        """ Class to decompose an wav file into its frequency vs. time spectrogram,
        and map that to piano keys.

        Args:
            decomposer (decomposer.Decomposer): with already precomputed self.chromagram
            scale (int): factor to resize origin image (from 1920x1080 resolution)
        """

        self.decomposer = decomposer
        self.fps_out = 30  # fps of output video

        # init a fresh piano img (use HSV if not using addWeighted func in _generate_keyboard, else RGB)
        piano_img = os.path.join('assets', 'piano.jpg')
        self.piano_template = Image.open(piano_img).convert('RGBA')

        # downsize for memory optimization
        self.piano_template = self.piano_template.resize(
            tuple(x // scale for x in self.piano_template.size), Image.ANTIALIAS
        )

        # output image sizes
        self.length_full = self.piano_template.size[0]  # length of a full frame
        self.keyboard_width = self.piano_template.size[1]  # size of keyboard in video
        self.width_full = self.length_full * 9 // 16  # expected width of a full frame (16:9 aspect ratio)

    def _generate_keyboard(self, t):
        """ Iterate through notes found in sample and draw on keyboard image.
        Intensity of color depends on loudness (decibels).
        All detected notes are stacked into a single image.

        Args:
            t (int): time point to generate keyboard frame for
        Returns:
            Tuple(np.ndarray, np.ndarray): image of colorized piano, piano roll slice

        """
        piano_out = self.piano_template.copy()
        piano_roll_slice = np.zeros((1, self.length_full, 3), dtype=np.uint8)

        key_number_array = np.nonzero(self.decomposer.chromagram_raw[:, t])[0]
        amp_array_non_zero = self.decomposer.chromagram_raw[key_number_array, t]
        if key_number_array.size > 0:
            amp_array_non_zero = self.decomposer._normalize_filter(amp_array_non_zero, algo=self.decomposer.norm_algo)

            # iterate through detected notes, extract location on keyboard if loudness thresh met
            for n in range(key_number_array.shape[0]):
                idx = 89 - key_number_array[n]
                loudness = amp_array_non_zero[n]

                if loudness > self.decomposer.amp_thresh:
                    piano_loc_points = self.decomposer.freq_table.iat[self.decomposer.last_key_num - 1 - idx, -1]
                    if type(piano_loc_points) is not list:
                        continue  # handle nan case

                    # fill in time vector for piano roll
                    piano_roll_slice[:, piano_loc_points[0][0]: piano_loc_points[-1][0], 1] = int(255 * loudness)

                    # color in detected note on keyboard img, stack onto output img
                    poly = Image.new('RGBA', (self.length_full, self.keyboard_width))
                    pdraw = ImageDraw.Draw(poly)
                    pdraw.polygon(piano_loc_points, fill=(0, 255, 0, int(255 * loudness)), outline=(0, 255, 240, 255))
                    piano_out.paste(poly, mask=poly)
        return np.array(piano_out.convert('RGB')), piano_roll_slice

    def build_movie(self):
        """ Concatenate self._full_frames images into video file, add back original music. """
        from moviepy.editor import AudioFileClip, ImageSequenceClip

        outname = self.decomposer.wav_file.replace('input', 'output')
        outname = outname.replace('wav', 'mp4')

        output = ImageSequenceClip(
            [self._generate_keyboard(t)[0] for t in range(self.decomposer.chromagram_raw.shape[1])], fps=self.fps_out/2
        )
        output = output.cutout(0, 1)  # trim to compensate for FFT lag
        output = output.set_audio(AudioFileClip(self.decomposer.wav_file))
        output.write_videofile(
            outname,
            fps=self.fps_out,
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            codec="libx264",
            audio_codec="aac"
        )