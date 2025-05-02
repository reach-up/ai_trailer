import logging
import os
import sys
from pathlib import Path
import src.common as common
import importlib


# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
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
        # Check if we need to run plot_retrieval
        from src.common import PLOT_PATH

        # If the plot file exists from the API request, skip plot_retrieval entirely
        if PLOT_PATH.exists():
            logger.info(
                "Plot already provided via API request, skipping plot_retrieval step"
            )
            # In this case we DON'T import or run plot_retrieval at all
        else:
            # Only run plot_retrieval if we don't have a plot yet
            logger.info("No plot found, attempting to retrieve plot from IMDB")
            # Only import the module if we need it
            try:
                plot_module = importlib.import_module("src.plot_retrieval")
                logger.info("Successfully imported plot_retrieval module")
            except Exception as e:
                logger.error("Failed to import plot_retrieval module: %s", str(e))
                raise

        # Step 2: Split the plot into subplots/scenes
        logger.info("Step 2: Generating subplots from main plot")
        run_module("subplot")

        # Reload common to refresh scene directories created by subplot
        try:
            import src.common as common

            importlib.reload(common)
            logger.info(
                "Reloaded src.common; updated SCENES_DIR count: %s",
                len(common.SCENES_DIR),
            )
        except Exception as e:
            logger.error("Failed to reload src.common: %s", e)

        # Step 3: Generate voice-overs for the subplots
        logger.info("Step 3: Generating voice-overs")
        run_module("voice")

        # Step 4: Generate frames from the subplots
        logger.info("Step 4: Generating frames")
        run_module("frame")

        # Step 5: Retrieve images based on the frames
        logger.info("Step 5: Retrieving images")
        run_module("image_retrieval")

        # Step 6: Create video clips for each frame
        logger.info("Step 6: Creating video clips")
        run_module("clip")

        # Step 7: Add audio to the video clips
        logger.info("Step 7: Adding audio to video clips")
        run_module("audio_clip")

        # Step 8: Join all clips to create the final trailer
        logger.info("Step 8: Joining clips to create final trailer")
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
        # Execute the module as a script by reloading the module
        # This is necessary for modules with code at the module level
        logger.info("Running module: %s", module_name)
        module_path = os.path.join(os.path.dirname(__file__), f"{module_name}.py")

        if not os.path.exists(module_path):
            raise FileNotFoundError(f"Module file not found: {module_path}")

        # Use exec to run the module contents
        with open(module_path, "r") as f:
            module_code = f.read()

        # Create a custom namespace for the module
        module_globals = {"__file__": module_path, "__name__": f"src.{module_name}"}

        # Execute the module code
        exec(module_code, module_globals)
        logger.info("Successfully completed module: %s", module_name)
    except (
        ImportError,
        ModuleNotFoundError,
        AttributeError,
        SyntaxError,
        FileNotFoundError,
    ) as e:
        logger.error("Error running module %s: %s", module_name, str(e))
        raise


if __name__ == "__main__":
    sys.exit(main())
