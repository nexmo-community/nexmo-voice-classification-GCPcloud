import os
import nexmo
import logzero
from logzero import logger
from config import huey

logzero.logfile("/tmp/nexmo-voice-classifier.log", maxBytes=1e6, backupCount=3)
nexmo_client = nexmo.Client(
    application_id=os.environ["APPLICATION_ID"], private_key=os.environ["PRIVATE_KEY"]
)


@huey.task()
def download_recording(recording_url, recording_uuid):
    logger.info(f"Download recording {recording_uuid}")

    recording = nexmo_client.get_recording(recording_url)
    recordingfile = f"./recordings/{recording_uuid}.mp3"
    os.makedirs(os.path.dirname(recordingfile), exist_ok=True)

    with open(recordingfile, "wb") as f:
        f.write(recording)

