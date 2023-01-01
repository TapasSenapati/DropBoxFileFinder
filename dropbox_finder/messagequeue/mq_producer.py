import logging
import os

import pika


LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL, format="%(asctime)s - %(levelname)s: %(message)s")


def add_message_for_processing(mq_connection, msg):
    # A channel provides a wrapper for interacting with RabbitMQ
    channel = mq_connection.channel()
    # Check for a queue and create it, if necessary
    channel.queue_declare(queue="add_files")
    # For the sake of simplicity, we are not declaring an exchange, so the subsequent publish call
    # will be sent to a Default exchange that is predeclared by the broker
    channel.basic_publish(
        exchange="",
        routing_key="add_files",
        properties=pika.BasicProperties(
            headers={"filename": msg["name"]}  # Add a key/value header
        ),
        body=msg["content"],
    )
    logging.info(
        "Added msg for %s of %s to message queue", msg["change_type"], msg["name"]
    )
