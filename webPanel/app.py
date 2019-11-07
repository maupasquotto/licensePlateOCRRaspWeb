from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
import docker
from os import getcwd
import base64
import json

# Vars
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
client = docker.from_env()
imgTempPath = 'temp/'


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/process_image', methods=['POST'])
def processImage():
    imgName = saveTempImage(request.json['image'])
    output = client.containers.run('openalpr/openalpr', '-c eu -j ' + imgName, remove=True, volumes={getcwd(): {'bind': '/data', 'mode': 'ro'}})
    socketio.emit('msg', {'data': json.loads(output)}, broadcast=True)
    return str(output)


@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)


@socketio.on('json')
def handle_json(jsonArg):
    print('received json: ' + str(jsonArg))


@socketio.on('connected')
def handle_connect_event(jsonArg):
    emit('msg', {'data': 'connected'})
    print('received json: ' + str(jsonArg))


def saveTempImage(encodedImage):
    meta = encodedImage.split(',')
    imgName = imgTempPath + 'img'

    # Get file extension
    if meta.__len__() == 2:
        encodedImage = meta[1]
        ext = '.' + meta[0].split(';')[0].split('/')[1]
        imgName += ext

    # Decode and save image
    imgdata = base64.b64decode(encodedImage)
    with open(imgName, 'wb') as f:
        f.write(imgdata)

    # Return image name
    return imgName


if __name__ == '__main__':
    socketio.run(app, debug=True)
