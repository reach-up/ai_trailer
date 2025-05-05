from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
import subprocess
import os
import json
import io
import base64
import yaml
import logging
from pathlib import Path
from starlette.requests import Request as StarletteRequest
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig
import torch.serialization

# Import from local modules
from src.common import MOVIES_DIR, TRAILER_DIR, configs

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
    # Get base URL for constructing absolute URLs
    base_url = str(request.base_url).rstrip('/')
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
            
        # Allow custom project name or generate one based on file ID and timestamp
        import time
        import uuid
        project_name = data.get("project_name") or f"project_{file_id[-6:]}_{int(time.time())}"
        
        # Clean project name to ensure it's valid for filesystem
        import re
        project_name = re.sub(r'[^\w-]', '_', project_name)
        logger.info(f"Creating trailer for project: {project_name}")
        
        # Create a copy of the default configs
        import copy
        project_configs = copy.deepcopy(configs)
        
        # Update config with project-specific values
        project_configs["project_name"] = project_name
        
        # Store video_id if provided (needed if the API-provided plot is missing)
        video_id = data.get("video_id")
        if video_id:
            project_configs["plot_retrieval"]["video_id"] = video_id

        # Set up project-specific paths
        from pathlib import Path
        project_dir = Path(f"{project_configs['project_dir']}/{project_name}")
        plot_path = project_dir / project_configs["plot_filename"]
        frames_dir = project_dir / "frames"
        trailer_dir = project_dir / "trailers"
        movies_dir = project_dir / project_configs["movies_dir"]
        
        # Create all needed directories
        for directory in [project_dir, frames_dir, trailer_dir, movies_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        
        # Save plot to the project-specific location
        plot_path.write_text(plot)
        logger.info("Saved plot to %s", plot_path)

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

        # Update configs with the project-specific video path
        project_configs["video_path"] = video_path
        
        # Save project-specific configs
        project_config_path = project_dir / "project_config.yaml"
        with open(project_config_path, "w") as f:
            yaml.safe_dump(project_configs, f)
        logger.info(f"Saved project config to {project_config_path}")

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

        try:
            # Run the subprocess with the project config path as an argument
            result = subprocess.run(
                ["python", "-m", "src.main", "--config", str(project_config_path)],
                check=True  # This will raise an exception if the process exits with non-zero status
            )
            
            logger.info("Trailer generation process completed with exit code %d", result.returncode)
            
            # Find the generated trailer file in the project-specific trailer directory
            trailer_path = trailer_dir / "final_trailer.mp4"
            
            if trailer_path.exists():
                logger.info("Found generated trailer at %s", trailer_path)
                # Return both the input video path and the trailer path
                return {
                    "status": "success", 
                    "project_name": project_name,
                    "input_video": video_path,
                    "trailer": str(trailer_path),
                    "download_url": f"{base_url}/download_trailer?project={project_name}"
                }
            else:
                logger.error("Trailer generation completed but no trailer file found at %s", trailer_path)
                return {
                    "status": "error", 
                    "message": "Trailer generation completed but no trailer file was found"
                }
            
        except subprocess.CalledProcessError as e:
            logger.error("Trailer generation failed with exit code %d", e.returncode)
            
            # Since we're not capturing output, we can't parse the error from process output
            # But the logs will be visible in the server console
            return {
                "status": "error",
                "message": "Trailer generation failed",
                "error": f"Process failed with exit code {e.returncode}",
                "log_available": True  # Indicate that full logs are available on the server
            }

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


@app.get("/download_trailer")
async def download_trailer(project: str):
    """Download the generated trailer file.
    
    Args:
        project: The project name to identify which trailer to download
    
    Returns:
        FileResponse: The trailer file as a downloadable response
    """
    logger.info("Trailer download requested for project: %s", project)
    
    # Construct the path to the trailer file
    project_dir = Path(f"{configs['project_dir']}/{project}")
    trailer_path = project_dir / "trailers" / "final_trailer.mp4"
    
    if not trailer_path.exists():
        logger.error("Requested trailer file not found: %s", trailer_path)
        return Response(content=f"Trailer file not found for project {project}", status_code=404)
    
    logger.info("Serving trailer file: %s", trailer_path)
    return FileResponse(
        path=str(trailer_path),
        filename=f"{project}_trailer.mp4",
        media_type="video/mp4"
    )
