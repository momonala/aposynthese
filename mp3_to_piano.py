from tqdm import tqdm
from moviepy.editor import *
from signal_process_utils import Song


song_file = os.path.join('assets', 'twinkle.mp3')
s = Song(song_file)

frames = []
sample_rate = 100
for offset in tqdm(range(0, s.ms, sample_rate)):
    sample_data = s.sample(offset=offset)
    piano_lit = s.generate_keyboard(sample_data)
    single_frame = ImageClip(f).set_duration(sample_rate / 1000.)
    frames.append(single_frame)

out = concatenate_videoclips(frames, method="compose")
out = out.set_audio(AudioFileClip(song_file))
# temp audio to dealth with moviepy bug
out.write_videofile("test.mp4",
                    fps=1000 // sample_rate,
                    temp_audiofile="temp-audio.m4a",
                    remove_temp=True,
                    codec="libx264",
                    audio_codec="aac"
                    )
