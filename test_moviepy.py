#!/usr/bin/env python3

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_moviepy")

logger.info("Testing MoviePy v2 imports and functionality")

try:
    # Import MoviePy using v2 style imports
    from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips
    logger.info("Successfully imported MoviePy components")
    logger.info(f"MoviePy version: {VideoFileClip.__module__.split('.')[0].__version__ if hasattr(VideoFileClip.__module__.split('.')[0], '__version__') else 'Unknown'}")
    
    # Print import paths to verify correct modules
    logger.info(f"VideoFileClip imported from: {VideoFileClip.__module__}")
    logger.info(f"AudioFileClip imported from: {AudioFileClip.__module__}")
    logger.info(f"CompositeAudioClip imported from: {CompositeAudioClip.__module__}")
    logger.info(f"concatenate_videoclips imported from: {concatenate_videoclips.__module__}")
    
    logger.info("All imports successful!")
    
except ImportError as e:
    logger.error(f"Import error: {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    sys.exit(1)

logger.info("Test completed successfully")
