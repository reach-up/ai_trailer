import logging
import shutil
import traceback
from pathlib import Path
from moviepy import VideoFileClip, concatenate_videoclips, AudioFileClip

from src.common import SCENES_DIR, TRAILER_DIR


def join_clips(all_scene_clips: list[list[Path]], trailer_dir: Path) -> None:
    """Join audio clips to create a single trailer.

    Args:
        all_scene_clips (list[list[Path]]): List of audio clips for each scene
        trailer_dir (Path): Directory to save the trailer
    """
    logger.info("\n===== Starting Trailer Generation =====")

    # Create a single trailer by selecting one clip from each scene
    trailer_clips = []

    for scene_idx, scene_clips in enumerate(all_scene_clips):
        if not scene_clips:
            logger.error(f"No clips found for scene {scene_idx+1}")
            continue

        # Select the first clip from each scene (assumed to be the best match)
        selected_clip_path = scene_clips[0]
        logger.info(f"Selected clip for scene {scene_idx+1}: {selected_clip_path}")

        if not selected_clip_path.exists():
            logger.error(f"Selected clip does not exist: {selected_clip_path}")
            continue

        try:
            # Make sure to include audio when loading the clip
            clip = VideoFileClip(str(selected_clip_path), audio=True)

            # Check if the clip has audio
            if clip.audio is None:
                logger.warning(f"Clip has no audio: {selected_clip_path}")
            else:
                logger.info(
                    f"Loaded clip with audio - Duration: {clip.duration}, Audio: {clip.audio.duration if clip.audio else 'None'}"
                )

            trailer_clips.append(clip)
        except Exception as e:
            logger.error(f"Failed to load clip {selected_clip_path}: {e}")

    if not trailer_clips:
        logger.error("No clips could be loaded for the trailer")
        return

    # Create the trailer path
    trailer_path = trailer_dir / "final_trailer.mp4"
    logger.info(f"Creating single trailer at: {trailer_path}")

    try:
        # Concatenate clips sequentially with audio
        logger.info(f"Concatenating {len(trailer_clips)} clips for the trailer")
        trailer = concatenate_videoclips(trailer_clips, method="compose")
        logger.info(f"Concatenation successful! Trailer duration: {trailer.duration}")

        # Write the trailer file with audio
        logger.info(f"Writing trailer to file: {trailer_path}")
        trailer.write_videofile(
            str(trailer_path),
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=str(trailer_dir / "temp-audio.m4a"),
            remove_temp=True,
        )
        logger.info(f"Successfully created trailer: {trailer_path}")
    except Exception as e:
        logger.error(f"Error creating trailer: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")

    logger.info("\n===== Trailer Generation Complete =====")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

logger.info("\n##### Starting step 7 trailer creation #####\n")

# Log scene directories
logger.info("Scene directories to process: %s", [str(d) for d in SCENES_DIR])

# Create trailer directory
if TRAILER_DIR.exists():
    logger.info("Removing existing trailer directory: %s", TRAILER_DIR)
    shutil.rmtree(TRAILER_DIR)

logger.info("Creating trailer directory: %s", TRAILER_DIR)
TRAILER_DIR.mkdir(parents=True, exist_ok=True)

# Discover audio clips for each scene
logger.info("Discovering audio clips in each scene directory...")
all_scene_clips = []
for scene_dir in SCENES_DIR:
    scene_audio_clips = list(scene_dir.glob("audio_clips/*.mp4"))
    logger.info(
        "Found %s audio clips in %s",
        len(scene_audio_clips),
        scene_dir,
    )
    all_scene_clips.append(scene_audio_clips)

# Start joining clips to create one final trailer
logger.info("Starting clip joining process to create one trailer...")
join_clips(all_scene_clips, TRAILER_DIR)
