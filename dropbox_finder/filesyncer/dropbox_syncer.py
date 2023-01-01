import logging
import os

import dropbox
from flask import jsonify

from dropbox_finder.clientutils.client_helpers import (
    get_dropbox_client,
    get_rabbitmq_connection,
    get_redis_connection,
)
from dropbox_finder.messagequeue.mq_producer import add_message_for_processing

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL, format="%(asctime)s - %(levelname)s: %(message)s")


def update_message_queue(account):
    """Call /files/list_folder for the given user ID and put changes into message queue to be processed.

    Args:
        account (str): DropBox account id
    """

    # Get redis ,rabbitmq and dropbox connections
    redis_connection = get_redis_connection(0)
    mq_connection = get_rabbitmq_connection()

    # OAuth token for the user
    token = "sl.BWCz30kDDdNUXopJj1kTnQG36AGw0o73njYaGi_12yf6BqhMZchOXBSnPGUZ6eFLXskDskk84eh9FuKjtI1VttpxXNqufYeJd0hg0XESGgWzkDcUFgo9ciUNtkSPAX405Qesrs8hJ2Y"

    # cursor for the user (None the first time)
    cursor = redis_connection.hget("cursors", account)

    dbx = get_dropbox_client(token)
    has_more = True

    try:
        while has_more:
            if cursor is None:
                result = dbx.files_list_folder(path="")
            else:
                result = dbx.files_list_folder_continue(cursor)

            for entry in result.entries:
                # Ignore deleted files, folders
                if isinstance(entry, dropbox.files.DeletedMetadata) or isinstance(
                    entry, dropbox.files.FolderMetadata
                ):
                    continue

                # Download the file
                file_name = entry.path_display
                # Download the file
                md, res = dbx.files_download(file_name)
                logging.info("Iterating file %s", entry.name)
                file_data = {}
                file_data["change_type"] = "addition"
                file_data["name"] = file_name
                file_data["content"] = res.content
                add_message_for_processing(mq_connection, file_data)

            # Update cursor
            cursor = result.cursor
            redis_connection.hset("cursors", account, cursor)

            # Repeat only if there's more to do
            has_more = result.has_more
    finally:
        # Close the connections
        redis_connection.close()
        dbx.close()
        mq_connection.close()
