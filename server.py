import os
import logzero
from logzero import logger
from flask import Flask, request, jsonify
from config import huey  # noqa
from tasks import download_recording

app = Flask(__name__)
logzero.logfile("/tmp/nexmo-voice-classifier.log", maxBytes=1e6, backupCount=3)


@app.route("/", methods=["GET"])
def ncco():
    logger.info(f"New call recieved from {request.args['from']}")
    return jsonify(
        [
            {"action": "talk", "text": "Record your message after the beep"},
            {
                "action": "record",
                "eventUrl": [f"{os.environ['BASE_URL']}/recordings"],
                "endOnKey": "*",
                "beepStart": True,
            },
        ]
    )


@app.route("/recordings", methods=["POST"])
def recordings_webhook():
    logger.info(f"Recording webhook called")
    recording_meta = request.get_json()

    download_recording(
        recording_meta["recording_url"], recording_meta["recording_uuid"]
    )

    return "OK"
