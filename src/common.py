import logging
import os
import re
from pathlib import Path

import yaml


def parse_configs(configs_path: str) -> dict:
    """Parse configs from the YAML file.

    Args:
        configs_path (str): Path to the YAML file

    Returns:
        dict: Parsed configs
    """
    configs = yaml.safe_load(open(configs_path, "r"))
    logger.info(f"Configs: {configs}")
    return configs


# Use the default configs path - no environment variable needed
CONFIGS_PATH = "configs.yaml"
logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)

logger.info("Using configuration file: %s", CONFIGS_PATH)
configs = parse_configs(CONFIGS_PATH)

PROJECT_DIR = Path(f"{configs['project_dir']}/{configs['project_name']}")
PLOT_PATH = PROJECT_DIR / configs["plot_filename"]
FRAMES_DIR = PROJECT_DIR / "frames"
TRAILER_DIR = PROJECT_DIR / "trailers"
MOVIES_DIR = PROJECT_DIR / configs["movies_dir"]

# Create essential directories if they don't exist
for directory in [PROJECT_DIR, FRAMES_DIR, TRAILER_DIR, MOVIES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
    logger.info(f"Directory ensured: {directory}")

SCENES_DIR = list(PROJECT_DIR.glob("scene_*"))
SCENES_DIR = sorted(
    SCENES_DIR, key=lambda s: int(re.search(r"\d+", str(s)).group())
)  # Natural sort
