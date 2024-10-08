import argparse
import socketio
import time
import os
import requests
from threading import Thread
import cv2


parser = argparse.ArgumentParser()
parser.add_argument("--video", default=0, type=int, help="Webcam index")
parser.add_argument("--server", default="http://localhost:5000")
args = parser.parse_args()

SERVER_URL = args.server
UPLOAD_ENDPOINT = "/upload"

sio = socketio.Client()

camera_index = args.video
output_dir = "./videos"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

is_recording = False
video_writer = None
recording_file_path = None

cap = cv2.VideoCapture(camera_index)
cap.set(cv2.CAP_PROP_FPS, 25)


def apply_camera_settings(settings):
    if settings:
        width = settings.get("width", 640)
        height = settings.get("height", 480)
        fps = settings.get("fps", 30)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, fps)
        print("Camera settings applied:", width, "x", height, "fps:", fps)


def start_recording():
    global is_recording, video_writer, recording_file_path, timestamp_file_path, timestamps
    if not is_recording:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        recording_file_path = os.path.join(
            output_dir, "recording_" + timestamp + "_" + str(args.video) + "_.mp4"
        )
        timestamp_file_path = os.path.join(
            output_dir, "recording_" + timestamp + "_" + str(args.video) + "_.txt"
        )
        timestamps = []

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        video_writer = cv2.VideoWriter(
            recording_file_path, fourcc, 25, (frame_width, frame_height)
        )
        is_recording = True
        print("Recording started:", recording_file_path)


def stop_recording():
    global is_recording, video_writer, timestamps, timestamp_file_path
    if is_recording:
        is_recording = False
        video_writer.release()
        print("Recording stopped and saved to", recording_file_path)

        # Save timestamps to the file
        with open(timestamp_file_path, "w") as f:
            for ts in timestamps:
                f.write(str(ts) + "\n")
        print("Timestamps saved to", timestamp_file_path)

        # Upload both video and timestamp files to the server
        upload_video_and_timestamps(recording_file_path, timestamp_file_path)


def upload_video_and_timestamps(video_path, timestamp_path):
    with open(video_path, "rb") as video_file, open(
        timestamp_path, "rb"
    ) as timestamp_file:
        files = {
            "video": (os.path.basename(video_path), video_file),
            "timestamps": (os.path.basename(timestamp_path), timestamp_file),
        }
        response = requests.post(SERVER_URL + UPLOAD_ENDPOINT, files=files)
        if response.status_code == 200:
            print("Video and timestamps uploaded successfully.")
        else:
            print("Failed to upload files. Status code:", response.status_code)


@sio.event
def connect():
    print("Connection established")


@sio.event
def disconnect():
    print("Disconnected from server")


@sio.on("camera_settings")
def on_camera_settings(data):
    apply_camera_settings(data)


@sio.on("start_recording")
def on_start_recording():
    start_recording()


@sio.on("stop_recording")
def on_stop_recording():
    stop_recording()


def capture_video():
    global is_recording, video_writer
    while True:
        ret, frame = cap.read()
        if ret:
            if is_recording:
                video_writer.write(frame)

                timestamp = time.time()
                timestamps.append(timestamp)

            cv2.imshow("Webcam Feed", frame)
            if cv2.waitKey(100) & 0xFF == ord("q"):
                break


# Connect to Socket.IO server
sio.connect(SERVER_URL)

# Start video capturing loop
video_thread = Thread(target=capture_video)
video_thread.start()

# Release resources on exit
video_thread.join()
cap.release()
cv2.destroyAllWindows()
sio.disconnect()
