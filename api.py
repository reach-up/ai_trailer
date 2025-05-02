from fastapi import FastAPI, Request
import subprocess
import os
import json
import io
import base64
import yaml
import logging
from pathlib import Path
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig
import torch.serialization

# Import from local modules
from src.common import MOVIES_DIR, configs

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Allow torch to safely load custom model objects
torch.serialization.add_safe_globals(
    [XttsConfig, XttsAudioConfig, BaseDatasetConfig, XttsArgs]
)

app = FastAPI()

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# We'll lazy-load the TTS model on first use to improve startup time
tts = None


def get_tts_model():
    global tts
    if tts is None:
        logger.info("Loading TTS model - this may take a moment...")
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
        logger.info("TTS model loaded successfully")
    return tts


@app.post("/generate_trailer")
async def generate_trailer(request: Request):
    try:
        data = await request.json()

        # Require plot parameter - no defaults
        if "plot" not in data or not data["plot"].strip():
            return {"error": "Missing or empty 'plot' parameter"}
        plot = data["plot"]

        # Require file_id parameter
        file_id = data.get("file_id")
        if not file_id:
            return {"error": "Missing 'file_id' parameter"}

        # Store video_id if provided but don't require it
        # (it's only needed if the API-provided plot is missing)
        video_id = data.get("video_id")

        # Only update the video_id in config if one was provided
        if video_id:
            configs["plot_retrieval"]["video_id"] = video_id

        # Make sure the project directory exists
        from src.common import PLOT_PATH, PROJECT_DIR

        # Ensure project directory exists
        PROJECT_DIR.mkdir(parents=True, exist_ok=True)

        # Save plot to the correct location
        PLOT_PATH.write_text(plot)
        logger.info("Saved plot to %s", PLOT_PATH)

        # The plot is now directly related to the video we'll download

        # Load service account credentials from environment secret
        SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
        if os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"):
            decoded = base64.b64decode(
                os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
            ).decode("utf-8")
            service_account_info = json.loads(decoded)
        else:
            raise RuntimeError("No service account env var provided.")
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=SCOPES
        )
        drive_service = build("drive", "v3", credentials=credentials)

        # Create a filename based on the file_id for uniqueness
        filename = f"input_{file_id[-6:]}.mp4"  # Use last 6 chars of ID for brevity
        video_path = str(MOVIES_DIR / filename)

        # Update configs with the actual video path that was used
        configs["video_path"] = video_path

        # Save updated configs for future reference
        with open("configs.yaml", "w") as f:
            yaml.safe_dump(configs, f)

        # Download video from Google Drive
        request_drive = drive_service.files().get_media(fileId=file_id)
        fh = io.FileIO(video_path, "wb")
        downloader = MediaIoBaseDownload(fh, request_drive)

        logger.info(
            "Starting video download from Google Drive with file_id: %s", file_id
        )
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                logger.info("Download progress: %d%%", int(status.progress() * 100))

        logger.info("Video successfully downloaded to: %s", video_path)

        # Run the main processing script
        # We need to run it in a way that allows it to find the src module
        # Use the -m flag to run the module as a package
        logger.info("Starting trailer generation process with main.py")

        # Run the subprocess and capture output
        subprocess.run(
            ["python", "-m", "src.main"], capture_output=True, text=True, check=True
        )

        # Check if the process completed successfully
        # if process.returncode != 0:
        #     logger.error("Trailer generation failed with error:\n%s", process.stderr)

        #     # Extract just the important error message without all the logs
        #     error_lines = process.stderr.split("\n")
        #     actual_error = "Unknown error"

        #     # Look for the actual error message (usually after ERROR or Exception)
        #     for line in error_lines:
        #         if "ERROR -" in line and "Error" in line:
        #             actual_error = line.split("ERROR -")[1].strip()
        #             break
        #         elif "Traceback" in line:
        #             # Find the last line of the traceback, which contains the actual error
        #             for i in range(len(error_lines) - 1, 0, -1):
        #                 if error_lines[i] and not error_lines[i].startswith(" "):
        #                     actual_error = error_lines[i].strip()
        #                     break
        #             break

        #     return {
        #         "status": "error",
        #         "message": "Trailer generation failed",
        #         "error": actual_error,
        #         "log_available": True,  # Indicate that full logs are available on the server
        #     }

        logger.info("Trailer generation complete")
        return {"status": "success", "video": video_path}
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON format: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


@app.get("/generate_trailer")
async def get_generate_trailer():
    return {
        "message": "This endpoint requires a POST request with the following JSON data:",
        "required_fields": [
            "plot: text description to use for the trailer",
            "file_id: Google Drive file ID of the video to use",
        ],
        "optional_fields": [
            "video_id: IMDB ID (only used as fallback if plot retrieval needs to be run)"
        ],
    }
