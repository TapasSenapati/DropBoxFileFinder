import logging
import os
import sys
from elasticsearch import Elasticsearch
from flask import jsonify
from text_parser import extract_data_from_path

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL, format="%(asctime)s - %(levelname)s: %(message)s")


def __create_client(host="localhost", port=9200):
    """
    Args:
        host (str, optional): Elastic Search host. Defaults to "localhost".
        port (int, optional): Elastic Search port. Defaults to 9200.
    Returns:
        es_client: Client to make requests to ElasticSearch cluster
    """
    es_client = Elasticsearch("http://{}:{}".format(host, port))
    try:
        es_client.info().body
    except Exception as e:
        logging.critical("There was an error completing dbt command.")
        sys.exit(10)
    return es_client


def index_data(local_path):
    """Index all data in local path into elasticsearch cluster
    Args:
        local_path (str): Path in local directory containing files to index
    """
    # Connect to the Elasticsearch cluster
    es_client = __create_client()
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
