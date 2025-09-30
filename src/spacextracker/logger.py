import logging

# Configure root logger
logging.basicConfig(
    level=logging.INFO,  # or DEBUG
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)

# Use the root logger or get a named one
logger = logging.getLogger("spacextracker")
logger.setLevel(logging.INFO)
