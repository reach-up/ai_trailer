import itertools
import logging
import shutil
from pathlib import Path

from moviepy import VideoFileClip, concatenate_videoclips

from src.common import SCENES_DIR, TRAILER_DIR


def join_clips(clip_combinations: list[tuple[str]], trailer_dir: Path) -> None:
    """Join audio clips to create a trailer.

    Args:
        clip_combinations (list[list[str]]): List of audio clips to be combined
        trailer_dir (Path): Directory save the trailers
    """
    logger.info("Total clip combinations: %s", len(clip_combinations))
    
    if not clip_combinations:
        logger.error("No clip combinations found. Check that audio clips were generated.")
        return
    
    for idx, clip_combination in enumerate(clip_combinations):
        logger.info("Generating trailer %s with %s clips", idx+1, len(clip_combination))
        
        if not clip_combination:
            logger.error("Empty clip combination found for trailer %s", idx+1)
            continue
            
        # Check that all clip paths exist
        valid_paths = []
        for clip_path in clip_combination:
            if Path(clip_path).exists():
                valid_paths.append(clip_path)
            else:
                logger.error("Clip path not found: %s", clip_path)
        
        if not valid_paths:
            logger.error("No valid clip paths found for trailer %s", idx+1)
            continue
            
        trailer_path = trailer_dir / f"trailer_{idx+1}.mp4"
        
        try:
            clips = [VideoFileClip(str(clip_path)) for clip_path in valid_paths]
            
            if not clips:
                logger.error("No clips could be loaded for trailer %s", idx+1)
                continue
                
            logger.info("Concatenating %s clips for trailer %s", len(clips), idx+1)
            trailer = concatenate_videoclips(clips)
            trailer.write_videofile(str(trailer_path))
        except Exception as e:
            logger.error("Error creating trailer %s: %s", idx+1, e)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

logger.info("\n##### Starting step 7 trailer creation #####\n")

if TRAILER_DIR.exists():
    shutil.rmtree(TRAILER_DIR)

TRAILER_DIR.mkdir(parents=True, exist_ok=True)

audio_clips = [list(scene_dir.glob("audio_clips/*.mp4")) for scene_dir in SCENES_DIR]
audio_clip_combinations = list(itertools.product(*audio_clips))

join_clips(audio_clip_combinations, TRAILER_DIR)
