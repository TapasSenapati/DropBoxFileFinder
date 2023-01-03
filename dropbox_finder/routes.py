import json
import logging
import os
import threading

from dotenv import load_dotenv, find_dotenv
from elasticsearch import Elasticsearch
from flask import Response, jsonify, request

from dropbox_finder import app
from dropbox_finder.clientutils.client_helpers import get_redis_connection
from dropbox_finder.filesyncer.dropbox_syncer import update_message_queue

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL, format="%(asctime)s - %(levelname)s: %(message)s")


@app.route("/")
@app.route("/login")
def main():
    # Extract and store the access token for this user
    load_dotenv(find_dotenv())
    ACCOUNT_ID = os.environ.get("ACCOUNT_ID")
    ACCOUNT_TOKEN = os.environ.get("ACCOUNT_TOKEN")
    logging.info("dbx acct id %s ", ACCOUNT_ID)
    logging.info("dbx oauth token %s ", ACCOUNT_TOKEN)
    redis_client = get_redis_connection()
    redis_client.hset("tokens", ACCOUNT_ID, ACCOUNT_TOKEN)
    redis_client.close()
    return "<h1 style='color:blue'>Hello.Please refer to https://github.com/TapasSenapati/DropBoxFileFinder for usage!</h1>"


@app.route("/sync")
def sync():
    update_message_queue(os.environ.get("ACCOUNT_ID"))
    return None


@app.route("/search")
def search():
    es = Elasticsearch("http://{}:{}".format("localhost", 9200))
    query = request.args.get("query")
    results = es.search(index="test-index", query={"match": {"text": query}})
    # Get the IDs of the matching documents
    ids = [hit["_id"] for hit in results["hits"]["hits"]]
    return jsonify(ids)


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
