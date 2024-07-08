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
	app.logger.info(data)
	app.logger.info(f"{data['username']} has seeked the video to {data['newTime']} in room {data['room']}")
	socketio.emit('video_seeked_announcement', data, room=data['room'])
	app.logger.info('sent video_seeked_announcement')
	
@socketio.on('video_paused')
def handle_video_pause(data):
	app.logger.info(f"{data['username']} has paused the video in room {data['room']}")
	socketio.emit('video_paused_announcement', data, room=data['room'])
	app.logger.info('sent video_paused_announcement')
	
@socketio.on('video_played')
def handle_video_play(data):
	app.logger.info(f"{data['username']} has played the video in room {data['room']}")
	socketio.emit('video_played_announcement', data, room=data['room'])
	app.logger.info('sent video_played_announcement')

@socketio.on('message')
def handle_new_message(data):
    if data['message'] not in ['/pause', '/play'] and '/alert' not in data['message']:
        app.logger.info(f"{data['username']} has send a new message room {data['room']}. Message: {data['message']}")
        socketio.emit('new_message_announcement', data, room=data['room'])
        app.logger.info('sent new_message_announcement')
    else:
        app.logger.info(f"{data['username']} has enter a {data['message']} command")
        if data['message'] == '/pause':
            socketio.emit('video_paused_announcement', data, room=data['room']) 
        elif data['message'] == '/play':
            socketio.emit('video_played_announcement', data, room=data['room'])
        elif '/alert' in data['message']:
            socketio.emit('send_alert', data, room=data['room'])

if __name__ == '__main__':
	socketio.run(app, host="0.0.0.0", debug=True)
