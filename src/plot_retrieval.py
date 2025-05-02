import logging

from imdb import Cinemagoer

from src.common import PLOT_PATH, configs


def get_video_plot(video_id) -> str:
    """Retrieve the video plot from IMDB.

    Args:
        video_id: Valid IMDB ID string in the format '0123456'

    Returns:
        str: Plot text from IMDB

    Raises:
        ValueError: If video_id is None or invalid
    """
    if not video_id or not isinstance(video_id, str):
        raise ValueError(f"A valid IMDB ID string is required, received: {video_id}")
        
    logger.info('Retrieving plot for IMDB ID: "%s"', video_id)
    ia = Cinemagoer()
    video = ia.get_movie(video_id)
    
    if not video or 'plot outline' not in video:
        raise ValueError(f"Could not retrieve plot for IMDB ID: {video_id}")
        
    plot = video['plot outline']
    PLOT_PATH.write_text(plot)
    logger.info('Successfully retrieved plot for IMDB ID: "%s"', video_id)
    
    return plot


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)

logger.info("\n##### Starting optional step plot retrieval #####\n")

# Ensure the parent directory exists
PLOT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Only try to retrieve a plot if we don't already have one
if not PLOT_PATH.exists():
    # Make sure we have a valid IMDB ID
    video_id = configs["plot_retrieval"].get("video_id")
    if not video_id:
        raise ValueError("No video_id provided in configuration. Cannot retrieve plot.")
    
    # Get the plot - this will raise an error if video_id is invalid
    plot = get_video_plot(video_id)
    logger.info('Retrieved plot from IMDB: "%s..."', plot[:100])
else:
    # If plot file already exists, read it and don't fetch from IMDB
    logger.info('Plot file already exists at %s, using existing plot', PLOT_PATH)
    plot = PLOT_PATH.read_text()
    logger.info('Using existing plot: "%s..."', plot[:100])
