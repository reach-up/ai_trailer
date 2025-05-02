import itertools
import logging
import shutil
import traceback
from pathlib import Path

from moviepy.editor import VideoFileClip, concatenate_videoclips

from src.common import SCENES_DIR, TRAILER_DIR


def join_clips(clip_combinations: list[tuple[str]], trailer_dir: Path) -> None:
    """Join audio clips to create a trailer.

    Args:
        clip_combinations (list[list[str]]): List of audio clips to be combined
        trailer_dir (Path): Directory save the trailers
    """
    logger.info("\n===== Starting Trailer Generation =====")
    logger.info("Total clip combinations to process: %s", len(clip_combinations))

    if not clip_combinations:
        logger.error(
            "No clip combinations found. Check that audio clips were generated."
        )
        return

    logger.info(
        "First clip combination content: %s",
        [str(p) for p in clip_combinations[0]] if clip_combinations else "None",
    )

    trailers_created = 0
    for idx, clip_combination in enumerate(clip_combinations):
        logger.info(
            "\n----- Processing trailer %s with %s clips -----",
            idx + 1,
            len(clip_combination),
        )

        if not clip_combination:
            logger.error("Empty clip combination found for trailer %s", idx + 1)
            continue

        # Check that all clip paths exist
        valid_paths = []
        invalid_paths = []
        for clip_path in clip_combination:
            path_obj = Path(clip_path)
            logger.info(
                "Checking clip path: %s (exists: %s)", clip_path, path_obj.exists()
            )
            if path_obj.exists():
                valid_paths.append(clip_path)
            else:
                invalid_paths.append(clip_path)
                logger.error("Clip path not found: %s", clip_path)

        logger.info("Valid paths: %s/%s", len(valid_paths), len(clip_combination))
        if invalid_paths:
            logger.error("Invalid paths: %s", invalid_paths)

        if not valid_paths:
            logger.error("No valid clip paths found for trailer %s", idx + 1)
            continue

        trailer_path = trailer_dir / f"trailer_{idx+1}.mp4"
        logger.info("Trailer will be saved to: %s", trailer_path)

        try:
            logger.info("Loading clips...")
            clips = []
            for i, clip_path in enumerate(valid_paths):
                try:
                    logger.info(
                        "Loading clip %s/%s: %s", i + 1, len(valid_paths), clip_path
                    )
                    clip = VideoFileClip(str(clip_path))
                    logger.info(
                        "Clip loaded - Duration: %s, Size: %s",
                        clip.duration,
                        getattr(clip, "size", "Unknown"),
                    )
                    clips.append(clip)
                except Exception as clip_error:
                    logger.error("Failed to load clip %s: %s", clip_path, clip_error)

            if not clips:
                logger.error("No clips could be loaded for trailer %s", idx + 1)
                continue

            logger.info("Concatenating %s clips for trailer %s", len(clips), idx + 1)
            try:
                trailer = concatenate_videoclips(clips)
                logger.info(
                    "Concatenation successful! Trailer duration: %s", trailer.duration
                )

                logger.info("Writing trailer to file: %s", trailer_path)
                trailer.write_videofile(str(trailer_path))

                trailers_created += 1
                logger.info("Successfully created trailer: %s", trailer_path)
            except Exception as concat_error:
                logger.error("Error in concatenation or writing: %s", concat_error)
                logger.error("Traceback: %s", traceback.format_exc())
        except Exception as e:
            logger.error("Error creating trailer %s: %s", idx + 1, e)
            logger.error("Traceback: %s", traceback.format_exc())

    logger.info("\n===== Trailer Generation Complete =====")
    logger.info("Successfully created %s trailers", trailers_created)


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

# Discover audio clips
logger.info("Discovering audio clips in each scene directory...")
audio_clips = []
for scene_dir in SCENES_DIR:
    scene_audio_clips = list(scene_dir.glob("audio_clips/*.mp4"))
    logger.info(
        "Found %s audio clips in %s: %s",
        len(scene_audio_clips),
        scene_dir,
        [f.name for f in scene_audio_clips],
    )
    audio_clips.append(scene_audio_clips)

# Generate combinations
logger.info("Generating clip combinations...")
audio_clip_combinations = list(itertools.product(*audio_clips))
logger.info("Generated %s clip combinations", len(audio_clip_combinations))

# Start joining clips
logger.info("Starting clip joining process...")
join_clips(audio_clip_combinations, TRAILER_DIR)
