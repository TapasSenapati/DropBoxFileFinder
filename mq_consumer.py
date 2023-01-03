import json
import logging
import os
import threading

from flask import jsonify

from dropbox_finder.clientutils.client_helpers import get_rabbitmq_connection

LOGLEVEL = os.environ.get("LOGLEVEL", "DEBUG").upper()
logging.basicConfig(level=LOGLEVEL, format="%(asctime)s - %(levelname)s: %(message)s")


# Since RabbitMQ works asynchronously, every time you receive a message, a
# callback function is called.
def sync_files_from_dropbox(ch, method, properties, body):
    """One way sync of files from dropbox folder to local dir.
    Args:
        local_path (str): Path in local system to store downloaded files.
    """
    logging.debug("Message body %s", json.loads(body))
    # md, res = dbx.files_download(file_name)
    ch.basic_ack(delivery_tag=method.delivery_tag)

    # List of synced files
    synced_files = []
    logging.debug("Synchronization complete")
    return jsonify(synced_files)


def process_messages():
    """read message from message queue regarding files modified"""

    logging.debug("Processing messages from queue.")
    mq_connection = get_rabbitmq_connection()
    # A channel provides a wrapper for interacting with RabbitMQ
    channel = mq_connection.channel()
    # Check for a queue to sync files
    channel.queue_declare(queue="sync_files")

    # Consume a message from a queue.
    channel.basic_consume(
        queue="sync_files", on_message_callback=sync_files_from_dropbox, auto_ack=True
    )
    logging.debug(" [*] Waiting for messages. To exit press CTRL+C")

    # Start listening for messages to consume
    channel.start_consuming()


# Create a new thread to start consuming messages from queue
consumer_thread = threading.Thread(target=process_messages)
consumer_thread.daemon = True
consumer_thread.start()
