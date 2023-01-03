import json
import logging
import os


LOGLEVEL = os.environ.get("LOGLEVEL", "DEBUG").upper()
logging.basicConfig(level=LOGLEVEL, format="%(asctime)s - %(levelname)s: %(message)s")


def add_message_for_processing(mq_connection, msg):
    """Put the file change metadata into the message queue

    Args:
        mq_connection (Object): Connection to rabbit mq server
        msg (json): json payload with file change metadata
    """
    # A channel provides a wrapper for interacting with RabbitMQ
    channel = mq_connection.channel()

    # Check for a queue and create it, if necessary
    channel.queue_declare(queue="sync_files")

    # For the sake of simplicity, we are not declaring an exchange, so the subsequent publish call
    # will be sent to the Default exchange that is pre declared by the broker
    channel.basic_publish(
        exchange="",
        routing_key="sync_files",
        body=json.dumps(msg, default=str),
    )
    logging.debug(
        "Added msg for %s of %s to message queue", msg["change_type"], msg["file_name"]
    )

    return ""
