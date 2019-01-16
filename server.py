import os

from flask import Flask, render_template, request, make_response, send_file, redirect, url_for

from mp3_to_piano import decomposer_pipeline

app = Flask(__name__)


@app.route('/', methods=['POST'])
def home(): 
	return render_template('homepage.html')


@app.route('/handle_data', methods=['POST'])
def handle_data():
	yt_base = 'https://www.youtube.com/watch?v='
	yt_link = request.form['yt_link']
	if yt_base not in yt_link:
		return render_template('homepage.html')

	decomposer_pipeline({'youtube': yt_link})
	return redirect(url_for('serve_video', yt_id=yt_link.split(yt_base)[-1]))


@app.route('/decomposed/<yt_id>')
def serve_video(yt_id):
	vid_path = os.path.join('output', yt_id + '.mp4')
	resp = make_response(send_file(vid_path, 'video/mp4'))
	resp.headers['Content-Disposition'] = 'inline'
	return resp


if __name__ == '__main__':
	app.run(debug=True)
