from fastapi import FastAPI, Request
import subprocess
import requests
import os
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig
import torch.serialization

 
torch.serialization.add_safe_globals([
    XttsConfig,
    XttsAudioConfig,
    BaseDatasetConfig,
    XttsArgs
])

app = FastAPI()

 
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

@app.post("/generate_trailer")
async def generate_trailer(request: Request):
    data = await request.json()
    plot = data.get("plot", "Default plot...")
    video_url = data.get("video_url")

     
    with open("plot.txt", "w") as f:
        f.write(plot)

     
    if video_url:
        video_path = "input_video.mp4"
        response = requests.get(video_url, stream=True)
        with open(video_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Video downloaded:", video_path)
    else:
        return {"error": "video_url is required"}

     
    subprocess.run(["python", "src/main.py"])

    return {"status": "started", "video": video_path}
