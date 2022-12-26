import logging
import os
from elasticsearch import Elasticsearch
from flask import Flask, jsonify, request

from dropbox_syncer import sync_files_from_dropbox, create_client
from es_helper import index_data

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL, format="%(asctime)s - %(levelname)s: %(message)s")
app = Flask(__name__)


@app.route("/sync")
def sync():
    local_path = request.args.get("local_path")
    is_dir = os.path.isdir(local_path)
    if not is_dir:
        logging.critical(
            "Not a valid local directory %s" + local_path
        )
        return jsonify("Not a valid local path")
    auth_token = request.args.get("auth_token")
    dbx_client = create_client(auth_token)
    response = sync_files_from_dropbox(local_path, dbx_client)
    return response


@app.route("/search")
def search():
    es = Elasticsearch("http://{}:{}".format("localhost", 9200))
    query = request.args.get("query")
    results = es.search(index="test-index", query={"match": {"text": query}})
    # Get the IDs of the matching documents
    ids = [hit["_id"] for hit in results["hits"]["hits"]]
    return jsonify(ids)


@app.route("/index")
def index():
    local_path = request.args.get("local_path")
    is_dir = os.path.isdir(local_path)
    if not is_dir:
        logging.critical(
            "Not a valid local directory %s" + local_path
        )
        return jsonify("Not a valid local path")
    response = index_data(local_path)
    # Return list of files parsed and indexed and error if any
    return response


if __name__ == "__main__":
    # client = create_client()
    # sync_files_from_dropbox(client, "D:\LocalRepo")
    app.run()
