import os
import logzero
from logzero import logger
from flask import Flask, request, jsonify
from config import huey  # noqa
from tasks import download_recording, transcribe_audio, classify_transcription

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
                "format": "wav",
                "endOnKey": "*",
                "beepStart": True,
            },
        ]
    )


@app.route("/recordings", methods=["POST"])
def recordings_webhook():
    logger.info(f"Recording webhook called")
    recording_meta = request.get_json()

    download_recording_task = download_recording.s(
        recording_meta["recording_url"], recording_meta["recording_uuid"]
    )

    pipeline = download_recording_task.then(transcribe_audio).then(
        classify_transcription
    )
    huey.enqueue(pipeline)

    return "All done :)"
