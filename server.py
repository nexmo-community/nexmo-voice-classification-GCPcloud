import os
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def ncco():
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
