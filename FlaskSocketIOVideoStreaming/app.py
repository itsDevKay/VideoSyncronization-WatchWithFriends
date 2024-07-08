import cv2
import base64
import io
from PIL import Image
import numpy as np
from flask_socketio import emit, SocketIO
from flask import Flask, render_template

app = Flask(__name__, template_folder="templates")
sio = SocketIO(app)

@sio.on('disconnect')
def disconnect():
    print('Client disconnected')
    emit('clear_guest_video', broadcast=True)

@sio.on('image')
def image(data):
    emit('response_back', { 'image': data['data_image'], 'uid': data['uid'] }, broadcast=True)

@app.route("/")
@app.route("/home")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    sio.run(app, debug=True, host="0.0.0.0", port=5555)