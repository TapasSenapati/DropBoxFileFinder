import logging
import os
from elasticsearch import Elasticsearch
from flask import jsonify
from dropbox_finder.clientutils.client_helpers import get_elastic_search_client
from dropbox_finder.textparser.text_parser import extract_data_from_path

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL, format="%(asctime)s - %(levelname)s: %(message)s")


def index_data(local_path):
    """Index all data in local path into elasticsearch cluster
    Args:
        local_path (str): Path in local directory containing files to index
    """
    # Connect to the Elasticsearch cluster
    es_client = get_elastic_search_client()
    files = os.listdir(local_path)
    for file in files:
        parsed = extract_data_from_path(os.path.join(local_path, file))
        # Extract the text and metadata from the parsed document
        text = parsed["content"]
        metadata = parsed["metadata"]

        # Index the extracted text and metadata in Elasticsearch
        try:
            es_client.index(
                index="test-index",
                id=file,
                document={"text": text, "metadata": metadata},
            )
        except Exception as e:
            logging.critical("There was an error indexing all the files")
            return jsonify(e)

        logging.info("Indexing file %s", file)

    logging.info("Done indexing all files in folder %s", local_path)
    return jsonify(filesIndexed=files)
