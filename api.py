from fastapi import FastAPI, Request
import subprocess
from TTS.api import TTS
import torch.serialization

 
torch.serialization.add_safe_globals(["TTS.tts.configs.xtts_config.XttsConfig"])

app = FastAPI()

 
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

@app.post("/generate_trailer")
async def generate_trailer(request: Request):
    data = await request.json()
    plot = data.get("plot", "Default plot...")

    with open("plot.txt", "w") as f:
        f.write(plot)

    subprocess.run(["python", "src/main.py"])
    return {"status": "started"}
