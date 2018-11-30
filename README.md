# musika

A tool to give anyone perfect pitch. 

Convert mp3 files into piano visualiztions by decomposing its underlying constituent frequencies. 

---

# Usage
`python mp3_to_piano.py [OPTIONS]`

### Options:
```
-h, --help      Print this help text and exit.
-s, --song      Name of the song in assets/ to transpose          default=None, type=str
-y, --youtube   URL of youtube video to transpose                 default=None, type=str
-m, --max_time  Time to process audio file until                  default=None, type=int
-p, --plot      Whether to plot the spectrograms for debugging    default=False, type=bool
```

# Installation
`pip install -r requirements.txt`
- Ensure [`ffmpeg`](https://www.ffmpeg.org/) is installed and added to your PATH for [pydub](https://github.com/jiaaro/pydub/) to work.

---

# How it Works 
Sound is a time signal: in the physical world, sound is how we interpret pressurve waves propogating through air over time. Digitially, this gets translated into an array, where the values represent the amplitude of the wave and the index is the time point. 

<img src="https://upload.wikimedia.org/wikipedia/commons/6/68/The_Elements_of_Sound_jpg.jpg" width="500" />
Sound Wave Plot from Wikipedia

If we want to extract the music notes from a song file, we need to know what frequencies are resonating at a each time point. [The Fourier Transform](https://en.wikipedia.org/wiki/Fourier_transform) is the mathematical operation to use to translate time signalw into frequency signals. Scipy's spectrogram method allows us to generate a plot shown below for a sound file, where the x-axis is time, the y-axis is frequency, and the color (or z-axis) is the relative intensity of that frequency/time value. Yellow is a higher intensity while blue is lower. The yellow spikes/lines therefore, are notes being played.

<img src="/assets/spectrogram.png" width="600" />

After applying peak detection at each time vector, we map the dominant frequencies at each time point to [notes on a music scale](https://en.wikipedia.org/wiki/Piano_key_frequencies).

<img src="/assets/fft.png" width="600" />

Fourier Transform (FFT) at a given time point, with peak detection

<img src="/assets/piano_sample.png" width="600" />

FFT dominant frequencies mapped to piano keys



If this pipeline is applied across all time points, we can generate a video like this:

![FINAL OUTPUT HERE](PIANO OUTUPT GIF HERE)](http://www.youtube.com/watch?v=YOUTUBE_VIDEO_ID_HERE)

# To Do
- test with more complex songs
- write 'how it works' blog post
- create better GUI than using OpenCV
- create guitar-hero like visualizaions for seeing future notes
- come up with a clever name
