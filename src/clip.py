import logging
import math
import shutil
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

import librosa
from moviepy import VideoFileClip

from src.common import SCENES_DIR, configs, PROJECT_DIR


def get_clip(video: VideoFileClip, min_clip_len: int) -> None:
    """Create video clips based on individual frames

    Args:
        video (VideoFileClip): Video file source for the clips
        min_clip_len (int): Minimum clip length
    """
    logger.info(
        "Starting clip creation with video: %s, min_clip_len: %s",
        video.filename,
        min_clip_len,
    )
    logger.info(
        "Video properties - duration: %s, fps: %s, size: %s",
        video.duration,
        video.fps,
        getattr(video, "size", "Unknown"),
    )

    fps = video.fps
    clips_created = 0

    for idx, scene_dir in enumerate(SCENES_DIR):
        logger.info("Generating clips for scene %s at path: %s", idx + 1, scene_dir)
        clip_dir = scene_dir / "clips"

        # Check for audio files - look in both scene dir and project audio dir
        scene_audio_dir = scene_dir / "audios"
        project_audio_dir = PROJECT_DIR / "audios"

        audio_filepaths = []
        if scene_audio_dir.exists():
            audio_filepaths.extend(list(scene_audio_dir.glob("*.wav")))
        if project_audio_dir.exists():
            audio_filepaths.extend(list(project_audio_dir.glob("*.wav")))

        logger.info("Found %s audio files for scene %s", len(audio_filepaths), idx + 1)

        # Check for frame files - look in both scene dir and project frames dir
        scene_frames_dir = scene_dir / "frames"
        project_frames_dir = PROJECT_DIR / "frames"

        frame_paths = []
        if scene_frames_dir.exists():
            frame_paths.extend(list(scene_frames_dir.glob("*.jpg")))
        if project_frames_dir.exists():
            frame_paths.extend(list(project_frames_dir.glob("*.jpg")))

        logger.info("Found %s frame files for scene %s", len(frame_paths), idx + 1)

        if clip_dir.exists():
            logger.info("Removing existing clip directory: %s", clip_dir)
            shutil.rmtree(clip_dir)

        logger.info("Creating clip directory: %s", clip_dir)
        clip_dir.mkdir(parents=True, exist_ok=True)

        scene_clips = 0
        for audio_filepath in audio_filepaths:
            audio_filename = audio_filepath.stem
            logger.info("Processing audio: %s", audio_filename)

            try:
                audio_duration = math.ceil(librosa.get_duration(path=audio_filepath))
                audio_duration = max(min_clip_len, audio_duration)
                logger.info("Audio duration: %s seconds", audio_duration)

                for frame_path in frame_paths:
                    frame = int(frame_path.stem.split("_")[-1])
                    logger.info("Processing frame: %s", frame)

                    clip_start = frame // fps
                    clip_end = min((clip_start + audio_duration), video.duration)
                    logger.info("Clip time range: %s to %s", clip_start, clip_end)

                    try:
                        logger.info(
                            "Creating subclip from %s to %s", clip_start, clip_end
                        )
                        clip = video.subclipped(clip_start, clip_end)

                        output_path = f"{clip_dir}/clip_{frame}_{audio_filename}.mp4"
                        logger.info("Writing clip to: %s", output_path)

                        clip.write_videofile(
                            output_path,
                            verbose=False,
                            logger=None,
                        )

                        scene_clips += 1
                        clips_created += 1
                        logger.info("Successfully created clip: %s", output_path)
                    except Exception as e:
                        logger.error("Error creating clip for frame %s: %s", frame, e)
            except Exception as e:
                logger.error("Error processing audio %s: %s", audio_filename, e)

        logger.info("Created %s clips for scene %s", scene_clips, idx + 1)

    logger.info("Clip creation complete. Total clips created: %s", clips_created)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

logger.info("\n##### Starting step 5 clip creation #####\n")

video = VideoFileClip(configs["video_path"], audio=True)

get_clip(video, configs["clip"]["min_clip_len"])
