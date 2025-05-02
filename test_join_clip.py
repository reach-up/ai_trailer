#!/usr/bin/env python3

import sys
import logging
import shutil
from pathlib import Path
import os
import tempfile

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_join_clip")

try:
    # Import MoviePy using v2 style imports
    from moviepy import VideoFileClip, concatenate_videoclips, ColorClip
    logger.info("Successfully imported MoviePy components")
    
    # Create temporary test directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        logger.info("Created temporary directory: %s", temp_path)
        
        # Create scene directories
        scene1_dir = temp_path / "scene1"
        scene1_dir.mkdir()
        
        scene2_dir = temp_path / "scene2"
        scene2_dir.mkdir()
        
        # Create audio_clips directories
        audio_clips1_dir = scene1_dir / "audio_clips"
        audio_clips1_dir.mkdir()
        
        audio_clips2_dir = scene2_dir / "audio_clips"
        audio_clips2_dir.mkdir()
        
        # Create trailers directory
        trailers_dir = temp_path / "trailers"
        trailers_dir.mkdir()
        
        logger.info("Created directory structure")
        
        # Create test clips
        clip1 = ColorClip(size=(320, 240), color=(255, 0, 0), duration=1)
        clip2 = ColorClip(size=(320, 240), color=(0, 255, 0), duration=1)
        
        # Save clips to appropriate locations
        clip1_path = str(audio_clips1_dir / "test_clip1.mp4")
        clip2_path = str(audio_clips2_dir / "test_clip2.mp4")
        
        logger.info("Saving test clips to: %s and %s", clip1_path, clip2_path)
        
        clip1.write_videofile(clip1_path, fps=24, logger=None)
        clip2.write_videofile(clip2_path, fps=24, logger=None)
        
        logger.info("Test clips saved successfully")
        
        # List of scene directories for our test
        scenes_dir = [scene1_dir, scene2_dir]
        
        # Define functions similar to join_clip.py
        def join_clips(clip_combinations, trailer_dir):
            """Join clips to create a trailer."""
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
                    logger.info("Loading clips:")
                    clips = []
                    for path in valid_paths:
                        logger.info("  Loading clip: %s", path)
                        clip = VideoFileClip(str(path))
                        clips.append(clip)
                        logger.info("  Clip loaded: %s, duration: %s, size: %s", 
                                  path, clip.duration, getattr(clip, 'size', 'Unknown'))
                    
                    if not clips:
                        logger.error("No clips could be loaded for trailer %s", idx+1)
                        continue
                        
                    logger.info("Concatenating %s clips for trailer %s", len(clips), idx+1)
                    trailer = concatenate_videoclips(clips)
                    
                    logger.info("Writing trailer to: %s", trailer_path)
                    trailer.write_videofile(str(trailer_path), fps=24)
                    
                    logger.info("Trailer written successfully: %s", trailer_path)
                except Exception as e:
                    logger.error("Error creating trailer %s: %s", idx+1, e)
        
        # Similar to audio_clips discovery in join_clip.py
        logger.info("Discovering audio clips in scenes directories")
        audio_clips = []
        for scene_dir in scenes_dir:
            clips = list(scene_dir.glob("audio_clips/*.mp4"))
            logger.info("Found %s audio clips in %s", len(clips), scene_dir)
            audio_clips.append(clips)
        
        # Generate all possible combinations (in this simple case, we just have one from each scene)
        import itertools
        audio_clip_combinations = list(itertools.product(*audio_clips))
        logger.info("Generated %s clip combinations", len(audio_clip_combinations))
        
        # Run the join_clips function
        join_clips(audio_clip_combinations, trailers_dir)
        
        # Check the results
        trailer_files = list(trailers_dir.glob("*.mp4"))
        logger.info("Found %s trailer files in %s", len(trailer_files), trailers_dir)
        
        for trailer_file in trailer_files:
            logger.info("Trailer file: %s, size: %s bytes", 
                      trailer_file, trailer_file.stat().st_size if trailer_file.exists() else 'Not found')

except ImportError as e:
    logger.error("Import error: %s", e)
    sys.exit(1)
except Exception as e:
    logger.error("Error during test: %s", e)
    import traceback
    logger.error("Traceback: %s", traceback.format_exc())
    sys.exit(1)

logger.info("Test completed successfully")
