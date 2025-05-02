import logging
import os
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for the AI trailer generation pipeline.
    Orchestrates the entire process of generating a trailer from a plot and video.
    """
    logger.info("Starting AI trailer generation pipeline")
    
    # Get the absolute path to the src directory
    src_dir = Path(__file__).parent.absolute()
    project_dir = src_dir.parent
    
    # Make sure we're working in the project directory
    os.chdir(project_dir)
    
    try:
        # Step 1: Process the plot to generate subplots
        logger.info("Step 1: Processing plot to generate subplots")
        run_module("plot_retrieval")
        
        # Step 2: Generate frames from the subplots
        logger.info("Step 2: Generating frames")
        run_module("frame")
        
        # Step 3: Retrieve images based on the frames
        logger.info("Step 3: Retrieving images")
        run_module("image_retrieval")
        
        # Step 4: Generate voice-overs for the subplots
        logger.info("Step 4: Generating voice-overs")
        run_module("voice")
        
        # Step 5: Create video clips for each frame
        logger.info("Step 5: Creating video clips")
        run_module("clip")
        
        # Step 6: Add audio to the video clips
        logger.info("Step 6: Adding audio to video clips")
        run_module("audio_clip")
        
        # Step 7: Join all clips to create the final trailer
        logger.info("Step 7: Joining clips to create final trailer")
        run_module("join_clip")
        
        logger.info("AI trailer generation completed successfully!")
        return 0
    except (ImportError, ModuleNotFoundError) as e:
        logger.error("Error during trailer generation: %s", str(e))
        return 1

def run_module(module_name):
    """
    Run a Python module from the src directory.
    
    Args:
        module_name (str): Name of the module to run (without .py extension)
    """
    try:
        # Import the module dynamically
        module = __import__(module_name)
        logger.info("Successfully completed module: %s", module_name)
    except (ImportError, ModuleNotFoundError, AttributeError, SyntaxError) as e:
        logger.error("Error running module %s: %s", module_name, str(e))
        raise

if __name__ == "__main__":
    sys.exit(main())
