import os
import nexmo
import logzero
from logzero import logger
from flask import Flask, request, jsonify

app = Flask(__name__)
logzero.logfile("/tmp/nexmo-voice-classifier.log", maxBytes=1e6, backupCount=3)
nexmo_client = nexmo.Client(
    application_id=os.environ["APPLICATION_ID"], private_key=os.environ["PRIVATE_KEY"]
)


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
    recording = nexmo_client.get_recording(recording_meta["recording_url"])

    recordingfile = f"./recordings/{recording_meta['recording_uuid']}.mp3"
    os.makedirs(os.path.dirname(recordingfile), exist_ok=True)

    with open(recordingfile, "wb") as f:
        f.write(recording)

    return "OK"
