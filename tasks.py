import os
import io
import nexmo
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
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
    recordingfile = f"./recordings/{recording_uuid}.wav"
    os.makedirs(os.path.dirname(recordingfile), exist_ok=True)

    with open(recordingfile, "wb") as f:
        f.write(recording)

    return {"recording_uuid": recording_uuid}


@huey.task()
def transcribe_audio(*args, recording_uuid):
    # Instantiates a client
    client = speech.SpeechClient()

    # The name of the audio file to transcribe
    file_name = f"./recordings/{recording_uuid}.wav"

    # Loads the audio into memory
    with io.open(file_name, "rb") as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    # Detects speech in the audio file
    logger.debug(f"Sending file for transcribing")
    response = client.recognize(config, audio)

    return {"transcript": response.results[0].alternatives[0].transcript}
