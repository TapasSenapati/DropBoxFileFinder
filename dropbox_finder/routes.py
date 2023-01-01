import json
import logging
import os

from elasticsearch import Elasticsearch
from flask import Flask, Response, jsonify, request

from dropbox_finder import app
from dropbox_finder.elasticsearch.es_helper import index_data
from dropbox_finder.filesyncer.dropbox_syncer import update_message_queue

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL, format="%(asctime)s - %(levelname)s: %(message)s")


@app.route("/")
def main():
    return "<h1 style='color:blue'>Hello There!</h1>"


@app.route("/sync")
def sync():
    local_path = request.args.get("local_path")
    is_dir = os.path.isdir(local_path)
    if not is_dir:
        logging.critical("Not a valid local directory %s" + local_path)
        return jsonify("Not a valid local path")
    auth_token = request.args.get("auth_token")
    dbx_client = create_client(auth_token)
    # response = sync_files_from_dropbox(local_path, dbx_client)
    return None


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
        logging.critical("Not a valid local directory %s" + local_path)
        return jsonify("Not a valid local path")
    response = index_data(local_path)
    # Return list of files parsed and indexed and error if any
    return response


@app.route("/webhook", methods=["GET"])
def verify():
    """Respond to the webhook verification from dropbox (GET request) by echoing back the challenge parameter."""

    resp = Response(request.args.get("challenge"))
    resp.headers["Content-Type"] = "text/plain"
    resp.headers["X-Content-Type-Options"] = "nosniff"

    return resp


@app.route("/webhook", methods=["POST"])
def webhook():
    """Receive a list of changed user IDs from Dropbox and process each."""

    for account in json.loads(request.data)["list_folder"]["accounts"]:
        update_message_queue(account)

    return ""
