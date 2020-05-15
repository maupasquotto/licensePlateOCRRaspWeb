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


@app.route('/process_image', methods=['POST'])  # For debugging only
def ppImage():
    return processImage(request.json)


@socketio.on('process_image')
def processImage(jsonArg):
    imgDecoded = ''
    try:
        imgDecoded = jsonArg['image']
        imgDecoded = imgDecoded.decode('utf-8')
    except Exception:
        pass

    imgName, imgData = saveTempImage(imgDecoded)
    output = client.containers.run('openalpr/openalpr', '-c eu -j ' + imgName, remove=True,
                                   volumes={getcwd(): {'bind': '/data', 'mode': 'ro'}})
    socketio.emit('new_tag', {'data': json.loads(output), 'img': imgData}, broadcast=True)
    return str(output)


@socketio.on('json')
def handle_json(jsonArg):
    print('received json: ' + str(jsonArg))


@socketio.on('connected')
def handle_connect_event(jsonArg):
    emit('msg', {'data': 'connected'})
    print('received json: ' + str(jsonArg))


@socketio.on('webResponse')
def handleWebResponse(data):
    socketio.emit('access', {'access': data['access']})
    print(str(data))


def saveTempImage(encodedImage):
    meta = encodedImage.split(',')
    imgBase64 = encodedImage
    imgName = imgTempPath + 'img'

    # Get file extension
    if meta.__len__() == 2:
        imgBase64 = meta[1]
        ext = '.' + meta[0].split(';')[0].split('/')[1]
        imgName += ext
    else:
        imgName += '.jpg'

    # Decode and save image
    imgdata = base64.b64decode(imgBase64)
    with open(imgName, 'wb') as f:
        f.write(imgdata)

    # Return image name
    return imgName, encodedImage


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
