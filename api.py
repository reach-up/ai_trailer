from fastapi import FastAPI, Request
import subprocess
import os
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig
import torch.serialization

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Allow specific classes for PyTorch unpickling
torch.serialization.add_safe_globals([
    XttsConfig,
    XttsAudioConfig,
    BaseDatasetConfig,
    XttsArgs
])

app = FastAPI()

# Load TTS model once
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

@app.post("/generate_trailer")
async def generate_trailer(request: Request):
    data = await request.json()
    plot = data.get("plot", "Default plot...")
    file_id = data.get("file_id")  # now using file_id, not URL

    if not file_id:
        return {"error": "file_id is required"}

    # Save the plot to plot.txt
    with open("plot.txt", "w") as f:
        f.write(plot)

    # Setup Google Drive API client
    SERVICE_ACCOUNT_FILE = "service_account.json"
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)

    # Prepare to download the video
    video_path = "input_video.mp4"
    request_drive = service.files().get_media(fileId=file_id)
    fh = io.FileIO(video_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request_drive)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")

    print("Video downloaded:", video_path)

    # Run the processing script
    subprocess.run(["python", "src/main.py"])

    return {"status": "started", "video": video_path}
