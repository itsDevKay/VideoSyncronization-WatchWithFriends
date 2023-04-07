import os

from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")


@app.route('/')
def index(): return render_template('index.html')

@app.route('/watch')
def watch_with_friends():
	username = request.args.get('username')
	room = request.args.get('room')

	if username and room: 
		return render_template('theater.html', username=username, room=room)
	return redirect(url_for('index'))

@socketio.on('join_room')
def handle_join_room(data):
	app.logger.info(f"{data['username']} has joined the room {data['room']}")
	join_room(data['room'])
	socketio.emit('join_room_announcement', data, room=data['room'])
	app.logger.info('sent join_room_announcement')

@socketio.on('video_seeked')
def handle_video_seek(data):
	app.logger.info(f"{data['username']} has seeked the video to {data['newTime']} in room {data['room']}")
	socketio.emit('video_seeked_announcement', data, room=data['room'])
	app.logger.info('sent video_seeked_announcement')

@socketio.on('message')
def handle_new_message(data):
	app.logger.info(f"{data['username']} has send a new message ro room {data['room']}. Message: {data['message']}")
	socketio.emit('new_message_announcement', data, room=data['room'])
	app.logger.info('sent new_message_announcement')

if __name__ == '__main__':
	socketio.run(app, debug=True)
