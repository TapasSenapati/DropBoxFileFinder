import logging
import os
from tika import parser

# Import the library to avoid warnings
import warnings

warnings.filterwarnings("ignore")

LOGLEVEL = os.environ.get("LOGLEVEL", "DEBUG").upper()
logging.basicConfig(level=LOGLEVEL, format="%(asctime)s - %(levelname)s: %(message)s")


def extract_data_from_message(msg):
    """
    Extract text content and metadata from files using the apache tika library

    Args:
        msg (String): Contents of the file in byte form

    Returns:
        results: A dictionary containing metadata,content and status of parsed file.
    """
    logging.debug("Parsing to string %s")
    # results = parser.from_buffer(base64.b64decode(msg["content"]))
    logging.debug("Extracting data for file %s", msg["file_name"])
    return results

