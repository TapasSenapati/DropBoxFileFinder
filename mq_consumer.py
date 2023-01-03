import json
import logging
import os
import threading

from dotenv import find_dotenv, load_dotenv

from dropbox_finder.clientutils.client_helpers import (
    get_dropbox_client,
    get_rabbitmq_connection,
)

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL, format="%(asctime)s - %(levelname)s: %(message)s")


# Since RabbitMQ works asynchronously, every time you receive a message, a
# callback function is called.
def sync_files_from_dropbox(ch, method, properties, body):
    """One way sync of files from dropbox folder to local dir."""
    msg = json.loads(body)
    logging.info("Message body %s", msg["file_name"])
    load_dotenv(find_dotenv())
    ACCOUNT_TOKEN = os.environ.get("ACCOUNT_TOKEN")
    dbx = get_dropbox_client(ACCOUNT_TOKEN)

    local_file_path = os.path.join("/home/downloads", msg["file_name"])

    if msg["change_type"] == "update":
        # download the updated file contents from dropbox and store it locally.
        try:
            md, res = dbx.files_download(msg["file_path"])
            logging.info("Downloading file %s", msg["file_name"])
        except Exception as e:
            logging.critical("Error while downloading %s ", e)

        file_content = res.content
        with open(local_file_path, "wb") as f:
            f.write(file_content)

    elif msg["change_type"] == "delete":
        # remove the file from local storage
        logging.info("Deleting file")
        if os.path.exists(local_file_path):
            os.remove(local_file_path)
            logging.info("%s file has been removed from local storage", local_file_path)
        else:
            logging.warning("The file does not exist")

    else:
        logging.warning("Invalid message put into queue")


def process_messages():
    """read message from message queue regarding files modified"""

    logging.info("Processing messages from queue.")
    mq_connection = get_rabbitmq_connection()
    # A channel provides a wrapper for interacting with RabbitMQ
    channel = mq_connection.channel()
    # Check for a queue to sync files
    channel.queue_declare(queue="sync_files")

    # Consume a message from a queue.
    channel.basic_consume(
        queue="sync_files", on_message_callback=sync_files_from_dropbox, auto_ack=True
    )
    logging.info(" [*] Waiting for messages. To exit press CTRL+C")

    # Start listening for messages to consume
    channel.start_consuming()


# Create a new thread to start consuming messages from queue
consumer_thread = threading.Thread(target=process_messages)
consumer_thread.start()
