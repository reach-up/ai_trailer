import logging
import math
import shutil
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

# Debug info about installed packages
logger.info("Python path: %s", sys.path)
logger.info("Installed packages: %s", sys.modules.keys())

try:
    import librosa
    logger.info("Successfully imported librosa")
except ImportError as e:
    logger.error("Failed to import librosa: %s", e)

try:
    import moviepy
    logger.info("Successfully imported moviepy. Version: %s", moviepy.__version__)
    from moviepy.editor import VideoFileClip
    logger.info("Successfully imported VideoFileClip from moviepy.editor")
except ImportError as e:
    logger.error("Failed to import moviepy: %s", e)
    # Try to install moviepy on the fly
    logger.info("Attempting to install moviepy...")
    import subprocess
    result = subprocess.run([sys.executable, "-m", "pip", "install", "moviepy"], capture_output=True, text=True)
    logger.info("Installation result: %s", result.stdout)
    logger.error("Installation error (if any): %s", result.stderr)
    try:
        import moviepy
        from moviepy.editor import VideoFileClip
        logger.info("Successfully installed and imported moviepy after pip install")
    except ImportError as e2:
        logger.error("Still failed to import moviepy after installation attempt: %s", e2)

from src.common import SCENES_DIR, configs


def get_clip(video: VideoFileClip, min_clip_len: int) -> None:
    """Create video clips based on individual frames

    Args:
        video (VideoFileClip): Video file source for the clips
        min_clip_len (int): Minimum clip length
    """
    fps = video.fps

    for idx, scene_dir in enumerate(SCENES_DIR):
        logger.info(f"Generating clips for scene {idx+1}")
        clip_dir = scene_dir / "clips"
        audio_filepaths = scene_dir.glob("audios/*.wav")
        frame_paths = scene_dir.glob("frames/*.jpg")

        if clip_dir.exists():
            shutil.rmtree(clip_dir)

        clip_dir.mkdir(parents=True, exist_ok=True)

        for audio_filepath in audio_filepaths:
            audio_filename = audio_filepath.stem
            audio_duration = math.ceil(librosa.get_duration(path=audio_filepath))
            audio_duration = max(min_clip_len, audio_duration)

            for frame_path in frame_paths:
                frame = int(frame_path.stem.split("_")[-1])

                clip_start = frame // fps
                clip_end = min((clip_start + audio_duration), video.duration)

                clip = video.subclip(clip_start, clip_end)

                clip.write_videofile(
                    f"{clip_dir}/clip_{frame}_{audio_filename}.mp4",
                    verbose=False,
                    logger=None,
                )
                # clip.close() # Sometimes the clip is closed before it finished writing


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

logger.info("\n##### Starting step 5 clip creation #####\n")

video = VideoFileClip(configs["video_path"], audio=True)

get_clip(video, configs["clip"]["min_clip_len"])
