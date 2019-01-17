import glob
import logging
import os

from flask import Flask, render_template, request, redirect, url_for, flash
from flask import Response, make_response, send_file

from mp3_to_piano import decomposer_pipeline, DecomposerError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'lol'

# globals:
yt_base = 'https://www.youtube.com/watch?v='
existing_files = [x.strip('.mp4').strip('output/') for x in glob.glob('output/*mp4')]


@app.route('/', methods=['GET', 'POST'])
def home(): 
	return render_template('homepage.html')


@app.route('/handle_data', methods=['POST'])
def handle_data():
	yt_link = request.form['yt_link']
	yt_id = yt_link.split(yt_base)[-1]
	if yt_base not in yt_link:
		msg = f'{yt_link} is not a valid YouTube ID'
		flash(msg)
		logger.error(f'SERVER >>>> {msg}')
		return render_template('homepage.html')

	if yt_id not in existing_files:
		logger.info(f'SERVER >>>> Song not found in database. Decomposing {yt_id}')
		try:
			decomposer_pipeline({'youtube': yt_link})
		except DecomposerError as de:
			flash(de.message)
			return render_template('homepage.html')
	else:
		logger.info(f'SERVER >>>> {yt_id} exists in database.')
	return redirect(url_for('serve_video', yt_id=yt_id))


# @app.route('/decomposed/<yt_id>')
# def serve_video(yt_id):
# 	def stream_video(chunksize=31457280):
# 		vid_path = os.path.join('output', yt_id + '.mp4')
# 		with open(vid_path, 'rb') as video_file:
# 			byte = video_file.read(chunksize)
# 			while byte:
# 				yield byte
# 	return Response(stream_video(), mimetype='video/mp4')


@app.route('/decomposed/<yt_id>')
def serve_video(yt_id):
	vid_path = os.path.join('output', yt_id + '.mp4')
	resp = make_response(send_file(filename_or_fp=vid_path, mimetype='video/mp4'))
	resp.headers['Content-Disposition'] = 'inline'
	resp.headers['Accept-Ranges'] = 'bytes'
	return resp


if __name__ == '__main__':
	app.run(debug=False, host='192.168.10.97', port=8000)
