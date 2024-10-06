# Camera Synchronization

📷🔄📸

## Install

Run the following command to install requirements python packages

```bash
pip install -r requirements.txt
```

## Run

1. Run the server app:

    ```bash
    python server.py
    ```

    Server runs on localhost with port 5000 as defaults. You can change host and port if you need.

1. Run the client app on another computer in the same network, Or on a new terminal in the same computer:

    ```bash
    python client.py
    ```

    Client waits for `start_recording` event.

1. Send the following API request using Postman or in a browser on the server computer to start camera recording operation:

    ```bash
    http://localhost:5000/start_recording
    ```

    And send the following API request to stop camera recording operation:

    ```bash
    http://localhost:5000/stop_recording
    ```

    The results will be save in the `videos` directory.
