import logging
import os
import sys

import dropbox
import pika
import redis
from elasticsearch import Elasticsearch

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL, format="%(asctime)s - %(levelname)s: %(message)s")


def get_redis_connection(db_num=0):
    redis_connection = redis.Redis(
        host="localhost", port=6379, db=db_num, charset="utf-8", decode_responses=True
    )
    return redis_connection


def get_elastic_search_connection(host="localhost", port=9200):
    """
    Args:
        host (str, optional): Elastic Search host. Defaults to "localhost".
        port (int, optional): Elastic Search port. Defaults to 9200.
    Returns:
        es_conn: Client to make requests to ElasticSearch cluster
    """
    es_conn = Elasticsearch("http://{}:{}".format(host, port))
    try:
        es_conn.info().body
    except Exception as e:
        logging.critical("There was an error setting up the elasticsearch connection.")
        sys.exit(10)
    return es_conn


def get_dropbox_client(auth_token):
    """
    Validates access token and generates a client
    Returns:
        dbx_client: Client to make api requests to Dropbox API
    """
    access_token = auth_token
    # Create a Dropbox API client using the access token
    dbx_client = dropbox.Dropbox(access_token)

    # Validate the access token by making a test API call
    try:
        dbx_client.users_get_current_account()
        logging.info("Dropbox access token is valid")
    except dropbox.exceptions.AuthError:
        logging.critical("Error: Invalid Dropbox access token")
        sys.exit(10)

    return dbx_client


def get_rabbitmq_connection():
    """
    Returns:
        mq_connection: connection to make produce/subscribe using rabbit mq
    """
    # If you want to have a more secure SSL authentication, use ExternalCredentials object instead
    credentials = pika.PlainCredentials(
        username="test", password="test", erase_on_connect=True
    )
    parameters = pika.ConnectionParameters(
        host="172.105.36.70", port=5672, credentials=credentials
    )
    # We are using BlockingConnection adapter to start a session.
    # It uses a procedural approach to using Pika and has most of the asynchronous expectations removed
    mq_connection = pika.BlockingConnection(parameters)
    return mq_connection
