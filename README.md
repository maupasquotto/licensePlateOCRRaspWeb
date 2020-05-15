# License plate OCR with raspberry 3 & OpenALPR

This project is divided in two major files,

This project was made as concept of a gate control (entrace control), where there is a computer server and a raspberry client.<br>
The Rasp can send images to the server, which uses a docker service with OpenALPR to recognise any license plate.<br>
There are two major functions on the 

**This project might not be suitable for production use.**

### Prerequisites
**Server:**
````text
docker pull openalpr/openalpr
pip install flask flask_socketio docker
python app.py
````

**Rasp:**
````text
pip install socketio pygame
python raspClient.py http://192.168.0.191:5000
````

It's needed to set the server IP in the rasp script.

### Project Pictures