import logging
import re
from pathlib import Path

import yaml


logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


def parse_configs(configs_path: str) -> dict:
    """Parse configs from the YAML file.

    Args:
        configs_path (str): Path to the YAML file

    Returns:
        dict: Parsed configs
    """
    with open(configs_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    logger.info("Loaded configs from %s", configs_path)
    return config_data


def initialize_with_config(project_configs: dict):
    """Initialize the common module with project-specific configuration.
    
    This function sets up all global variables needed for the trailer generation
    process based on the provided configuration.
    
    Args:
        project_configs (dict): Project-specific configuration dictionary
    """
    # pylint: disable=global-statement
    global configs, PROJECT_DIR, PLOT_PATH, FRAMES_DIR, TRAILER_DIR, MOVIES_DIR, SCENES_DIR
    
    # Store the configuration
    configs = project_configs
    logger.info("Initialized with project: %s", configs['project_name'])
    
    # Set up project directories
    PROJECT_DIR = Path(f"{configs['project_dir']}/{configs['project_name']}")
    PLOT_PATH = PROJECT_DIR / configs["plot_filename"]
    FRAMES_DIR = PROJECT_DIR / "frames"
    TRAILER_DIR = PROJECT_DIR / "trailers"
    MOVIES_DIR = PROJECT_DIR / configs["movies_dir"]
    
    logger.info("Project directory: %s", PROJECT_DIR)
    logger.info("Plot path: %s", PLOT_PATH)
    
    # Create essential directories if they don't exist
    project_dirs = [PROJECT_DIR, FRAMES_DIR, TRAILER_DIR, MOVIES_DIR]
    for proj_dir in project_dirs:
        proj_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Directory ensured: %s", proj_dir)
    
    # Look for scene directories
    update_scenes_dir()


def update_scenes_dir():
    """Update the SCENES_DIR global variable based on current PROJECT_DIR.
    
    This function is used to refresh the list of scene directories, especially
    after new scenes have been created during the trailer generation process.
    """
    # pylint: disable=global-statement
    global SCENES_DIR
    SCENES_DIR = list(PROJECT_DIR.glob("scene_*"))
    SCENES_DIR = sorted(
        SCENES_DIR, key=lambda s: int(re.search(r"\d+", str(s)).group())
    )  # Natural sort
    logger.info("Found %s scene directories", len(SCENES_DIR))


# Load default configuration if not being initialized with a specific project config
# This will be overridden if initialize_with_config is called
CONFIGS_PATH = "configs.yaml"
logger.info("Loading default configuration from: %s", CONFIGS_PATH)
configs = parse_configs(CONFIGS_PATH)

# Set up default paths
PROJECT_DIR = Path(f"{configs['project_dir']}/{configs['project_name']}")
PLOT_PATH = PROJECT_DIR / configs["plot_filename"]
FRAMES_DIR = PROJECT_DIR / "frames"
TRAILER_DIR = PROJECT_DIR / "trailers"
MOVIES_DIR = PROJECT_DIR / configs["movies_dir"]

# Create essential directories if they don't exist
for directory in [PROJECT_DIR, FRAMES_DIR, TRAILER_DIR, MOVIES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
    logger.info(f"Directory ensured: {directory}")

# Initialize scenes directory
SCENES_DIR = list(PROJECT_DIR.glob("scene_*"))
SCENES_DIR = sorted(
    SCENES_DIR, key=lambda s: int(re.search(r"\d+", str(s)).group())
)  # Natural sort
