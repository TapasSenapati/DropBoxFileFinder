import json
import logging
import os
from elasticsearch import Elasticsearch
from flask import jsonify
from dropbox_finder.clientutils.client_helpers import get_elastic_search_connection
from dropbox_finder.textparser.text_parser import extract_data_from_message

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL, format="%(asctime)s - %(levelname)s: %(message)s")


def add_doc_to_index(local_path):
    """Index/update document into elasticsearch cluster
    """
    # Connect to the Elasticsearch cluster
    es_client = get_elastic_search_connection()
    parsed = extract_data_from_message(local_path)
    # Extract the text and metadata from the parsed document
    text = parsed["content"]
    metadata = parsed["metadata"]
    file_name = os.path.basename(local_path)

    # Index the extracted text and metadata in Elasticsearch
    try:
        res = es_client.index(
            index="test-index",
            id=file_name,
            document={"text": text, "metadata": metadata},
        )
    except Exception as e:
        logging.critical("There was an error indexing the file")

    logging.info("Done Indexing file %s", file_name)
    es_client.close()

def remove_doc_from_index(local_path):
    """Remove document from elasticsearch cluster
    """
    # Connect to the Elasticsearch cluster
    es_client = get_elastic_search_connection()
    file_name = os.path.basename(local_path)

    # Check if the document exists
    if es_client.exists(index='test-index', id=file_name):
        # Delete the document
        res = es_client.delete(index='test-index', id=file_name)
    else:
        logging.warning('File/Index does not exist')
    
    logging.info("Done removing document %s from es cluster", file_name)
    es_client.close()