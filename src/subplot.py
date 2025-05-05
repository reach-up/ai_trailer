import logging
import shutil

from src.common import PLOT_PATH, PROJECT_DIR, configs


def get_sub_plots(plot: str, split_char: str) -> None:
    """Split the plot into subplots (scenes).

    Args:
        plot (str): Plot text
        split_char (str): Character used to split the main plot
    """
    logger.info(f"Generating subplots using split character: '{split_char}'")
    logger.info(f"Original plot: '{plot}'")
    
    # First handle the plot by lines
    subplots = [line.strip() for line in plot.splitlines() if line.strip()]
    
    # If we have a split character, further split each line by that character
    if split_char:
        split_subplots = []
        for line in subplots:
            # Split by the character
            parts = [part.strip() for part in line.split(split_char) if part.strip()]
            # Add back the split character for natural reading
            parts = [f"{part}{split_char}" for part in parts]
            split_subplots.extend(parts)
        subplots = split_subplots
    
    # Handle case where we end up with no subplots
    if not subplots:
        logger.warning("No subplots were generated after splitting. Using full plot as one scene.")
        subplots = [plot]
    
    logger.info(f"Created {len(subplots)} subplots: {subplots}")

    # Create scene directories with subplot files
    for idx, subplot in enumerate(subplots):
        scene_dir = PROJECT_DIR / f"scene_{idx+1}"
        scene_plot_path = scene_dir / "subplot.txt"

        # Clean up any existing directory
        if scene_dir.exists():
            shutil.rmtree(scene_dir)

        scene_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created scene directory: {scene_dir}")
        
        # Write the subplot text
        scene_plot_path.write_text(subplot)
        logger.info(f"Saved subplot to {scene_plot_path}: '{subplot}'")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

logger.info("\n##### Starting step 1 subplot generation #####\n")

# Log information about the current project
logger.info(f"Using project directory: {PROJECT_DIR}")
logger.info(f"Reading plot from: {PLOT_PATH}")

# Read the plot file
try:
    plot = PLOT_PATH.read_text()
    logger.info(f"Successfully read plot with length: {len(plot)}")
    
    # Process the subplots
    get_sub_plots(plot, configs["subplot"]["split_char"])
    
    # Update the scene directories in common module
    from src.common import update_scenes_dir
    update_scenes_dir()
    logger.info("Updated scene directories in common module")
    
except Exception as e:
    logger.error(f"Error in subplot generation: {e}")
    import traceback
    logger.error(traceback.format_exc())
    raise
