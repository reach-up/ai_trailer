from fastapi import FastAPI, Request
import subprocess
import os
import json
import io

from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig
import torch.serialization

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Allow torch to safely load custom model objects
torch.serialization.add_safe_globals([
    XttsConfig,
    XttsAudioConfig,
    BaseDatasetConfig,
    XttsArgs
])

app = FastAPI()

# Load TTS model once at startup
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

@app.post("/generate_trailer")
async def generate_trailer(request: Request):
    data = await request.json()
    plot = data.get("plot", "Default plot...")
    file_id = data.get("file_id")

    if not file_id:
        return {"error": "Missing file_id"}

    # Save plot to file
    with open("plot.txt", "w") as f:
        f.write(plot)

    # Load service account credentials from environment secret
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=credentials)

    # Download video from Google Drive
    video_path = "input_video.mp4"
    request_drive = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(video_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request_drive)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"Download progress: {int(status.progress() * 100)}%")

    print("Video downloaded:", video_path)

    # Run processing script
    subprocess.run(["python", "src/main.py"])

    return {"status": "started", "video": video_path}
