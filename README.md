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
-p, --plot      Whether to plot the spectrograms for debugging    default=False, type=bool
```

# Installation
`pip install -r requirements.txt`
- Ensure [`ffmpeg`](https://www.ffmpeg.org/) is installed and added to your PATH for [pydub](https://github.com/jiaaro/pydub/) to work.

# To Do
- test with more complex songs
- write 'how it works' blog post
- create better GUI than using OpenCV
- create guitar-hero like visualizaions for seeing future notes
- come up with a clever name
