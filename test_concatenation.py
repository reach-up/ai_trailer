#!/usr/bin/env python3

import sys
import logging
from pathlib import Path
import tempfile
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_concatenation")

logger.info("Testing MoviePy v2 video concatenation")

try:
    # Import MoviePy components
    from moviepy import VideoFileClip, concatenate_videoclips
    logger.info("Successfully imported MoviePy components")
    
    # Create a temporary directory for our test
    with tempfile.TemporaryDirectory() as temp_dir:
        logger.info(f"Created temporary directory: {temp_dir}")
        
        # Create a couple of very small test clips using ColorClip
        from moviepy import ColorClip
        
        test_clip1 = ColorClip(size=(320, 240), color=(255, 0, 0), duration=1)
        test_clip2 = ColorClip(size=(320, 240), color=(0, 255, 0), duration=1)
        
        logger.info("Created test clips")
        
        # Save the test clips
        clip1_path = os.path.join(temp_dir, "clip1.mp4")
        clip2_path = os.path.join(temp_dir, "clip2.mp4")
        
        test_clip1.write_videofile(clip1_path, fps=24, logger=None)
        test_clip2.write_videofile(clip2_path, fps=24, logger=None)
        
        logger.info(f"Saved test clips to {clip1_path} and {clip2_path}")
        
        # Now load the clips from disk
        clip1 = VideoFileClip(clip1_path)
        clip2 = VideoFileClip(clip2_path)
        
        logger.info("Loaded clips from disk")
        
        # Concatenate the clips
        logger.info("Attempting to concatenate clips...")
        final_clip = concatenate_videoclips([clip1, clip2])
        logger.info("Concatenation successful!")
        
        # Write the final clip
        final_path = os.path.join(temp_dir, "final.mp4")
        final_clip.write_videofile(final_path, fps=24, logger=None)
        logger.info(f"Final concatenated clip written to {final_path}")
        
        # Close all clips to free resources
        clip1.close()
        clip2.close()
        final_clip.close()
    
except ImportError as e:
    logger.error(f"Import error: {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Error during test: {e}")
    sys.exit(1)

logger.info("Test completed successfully")
