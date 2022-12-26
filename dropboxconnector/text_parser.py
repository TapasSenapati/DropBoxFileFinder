import logging
import os
from tika import parser

# Import the library to avoid warnings
import warnings

warnings.filterwarnings("ignore")

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL, format="%(asctime)s - %(levelname)s: %(message)s")


def extract_data_from_path(file_path):
    """
    Extract text content and metadata from files using the apache tika library

    Args:
        file_path (String): Path in local system pointing to the file

    Returns:
        results: A dictionary containing metadata,content and status of parsed file.
    """
    results = parser.from_file(file_path)
    logging.info("Parsing file %s", file_path)
    return results

