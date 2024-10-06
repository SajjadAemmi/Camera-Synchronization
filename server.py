from flask import Flask, request
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)


@app.route("/")
def index():
    return "WebSocket server running"


# Endpoint to trigger start recording
@app.route("/start_recording", methods=["GET"])
def start_recording():
    socketio.emit("start_recording")  # Broadcast to all clients
    return "Recording started"


# Endpoint to trigger stop recording
@app.route("/stop_recording", methods=["GET"])
def stop_recording():
    socketio.emit("stop_recording")  # Broadcast to all clients
    return "Recording stopped"


@socketio.on("connect")
def handle_connect():
    print("Client connected")


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
